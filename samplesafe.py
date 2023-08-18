
import os
import io
import numpy as np
import soundfile as sf
import ffmpeg
from pydub import AudioSegment

def process_lossless_audio(file_path, verbose=False):
    data, samplerate = sf.read(file_path)
    channels = data.shape[1] if len(data.shape) > 1 else 1
    fade_duration_samples = int(0.005 * samplerate)
    for ch in range(channels):
        channel_data = data[:, ch] if channels > 1 else data
        if channel_data[0] != 0:
            fade_curve = np.linspace(0, 1, fade_duration_samples)
            channel_data[:fade_duration_samples] *= fade_curve
        if channel_data[-1] != 0:
            fade_curve = np.linspace(1, 0, fade_duration_samples)
            channel_data[-fade_duration_samples:] *= fade_curve
    subtype = 'PCM_24'
    return data, samplerate, subtype

def process_mp3_start_end(file_path, verbose=False):
    probe = ffmpeg.probe(file_path)
    bitrate = int(probe['streams'][0]['bit_rate'])
    samplerate = int(probe['streams'][0]['sample_rate'])
    duration = float(probe['streams'][0]['duration'])
    fade_duration = 0.005
    fade_duration = min(fade_duration, duration / 2)
    start_audio, _ = (
        ffmpeg.input(file_path)
        .output('pipe:', format='wav', t=fade_duration)
        .run(capture_stdout=True, capture_stderr=True)
    )
    end_audio, _ = (
        ffmpeg.input(file_path)
        .output('pipe:', format='wav', ss=duration - fade_duration, t=fade_duration)
        .run(capture_stdout=True, capture_stderr=True)
    )
    start_segment = AudioSegment.from_wav(io.BytesIO(start_audio))
    end_segment = AudioSegment.from_wav(io.BytesIO(end_audio))
    if len(start_segment) > 0 and start_segment.get_array_of_samples()[0] != 0:
        start_segment = start_segment.fade_in(int(fade_duration * 1000))
    if len(end_segment) > 0 and end_segment.get_array_of_samples()[-1] != 0:
        end_segment = end_segment.fade_out(int(fade_duration * 1000))
    start_mp3 = start_segment.export(format="mp3", bitrate=f"{bitrate // 1000}k")
    end_mp3 = end_segment.export(format="mp3", bitrate=f"{bitrate // 1000}k")
    
    start_mp3_path = os.path.join(os.path.dirname(file_path), 'temp_start_mp3.mp3')
    end_mp3_path = os.path.join(os.path.dirname(file_path), 'temp_end_mp3.mp3')
    with open(start_mp3_path, 'wb') as f:
        f.write(start_mp3.read())
    with open(end_mp3_path, 'wb') as f:
        f.write(end_mp3.read())
    return start_mp3_path, end_mp3_path
    

def concatenate_mp3_parts(original_mp3_path, start_mp3_path, end_mp3_path, fade_duration=0.005, verbose=False):
    probe = ffmpeg.probe(original_mp3_path)
    duration = float(probe['streams'][0]['duration'])
    main_body_duration = duration - 2 * fade_duration
    main_body_mp3_path = os.path.join(os.path.dirname(original_mp3_path), 'mp3_main_body.mp3')
    (
        ffmpeg.input(original_mp3_path, ss=fade_duration, t=main_body_duration)
        .output(main_body_mp3_path, c='copy')
        .run(overwrite_output=True)
    )
    output_mp3_path = original_mp3_path.replace('.mp3', '_samplesafe.mp3')
    (
        ffmpeg.input('concat:' + start_mp3_path + '|' + main_body_mp3_path + '|' + end_mp3_path)
        .output(output_mp3_path, c='copy')
        .run(overwrite_output=True)
    )
    
    # Cleanup temporary files
    os.remove(start_mp3_path)
    os.remove(end_mp3_path)
    
    
    # Cleanup main body temporary file
    os.remove(main_body_mp3_path)
    return output_mp3_path
    
    


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process audio files to ensure they start and end at zero-crossing points.')
    parser.add_argument('input_file', type=str, help='Path to the audio file to process.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging.')
    args = parser.parse_args()

    # Determine file type and call appropriate function
    file_extension = os.path.splitext(args.input_file)[-1].lower()
    
    if file_extension == ".wav":
        processed_data, samplerate, subtype = process_lossless_audio(args.input_file, args.verbose)
        output_file_name = args.input_file.replace('.wav', '_samplesafe.wav')
        sf.write(output_file_name, processed_data, samplerate, subtype=subtype)
        if args.verbose:
            print(f"Processed WAV file saved as: {output_file_name}")

    elif file_extension == ".mp3":
        start_mp3, end_mp3 = process_mp3_start_end(args.input_file, args.verbose)
        output_mp3_path = concatenate_mp3_parts(args.input_file, start_mp3, end_mp3, verbose=args.verbose)
        if args.verbose:
            print(f"Processed MP3 file saved as: {output_mp3_path}")
        
        # Cleanup temporary files
        
        
        

    else:
        print(f"Unsupported file type: {file_extension}. The tool currently supports WAV and MP3 files.")
