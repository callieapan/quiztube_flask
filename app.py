from flask import Flask, render_template, request
import os
import whisper
from moviepy.editor import VideoFileClip
from pytube import YouTube


app = Flask(__name__)
# directory paths
video_dir_path = './video_files/'
audio_dir_path = './audio_files/'

whisper_model = whisper.load_model("base")

#helper functions
def download_youtube_video(url, save_path):
    try:
        # Create a YouTube object
        yt = YouTube(url)

        # Get the highest resolution stream available
        stream = yt.streams.get_highest_resolution()

        # Download the video
        stream.download(output_path=save_path)

        print(f"Video downloaded successfully and saved to {save_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def get_mp4_filename(source_folder):
    try:
        # Get the list of files in the source folder
        files = os.listdir(source_folder)
        
        # Find the first file with .mp4 extension
        for file in files:
            if file.endswith('.mp4'):
                #print(file)
                return file  # Exit after copying the first .mp4 file
        print("No .mp4 file found in the source folder.")
    except Exception as e:
        print(f"An error occurred: {e}")
        
def gen_audio_path(video_filename, audio_dir_path):
    #extract filename without extension
    ind = video_filename.find('.mp4')
    audio_file_path = audio_dir_path+video_filename[:ind]+".wav"
    return audio_file_path


def extract_audio_from_video(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    return f'Hello, {name}!'

@app.route('/transcribe_video', methods=['POST'])

def transcribe_video():
    video_url = request.args.get('video_url')
    # Local path where the video will be saved
    dirname = "video"+"_"+video_url[-4:]
    video_save_path = video_dir_path+dirname
    
    # Download the video 
    download_youtube_video(video_url, video_save_path)

    #obtain video filename
    video_filename = get_mp4_filename(video_save_path)
    #construct video file path and audio path
    video_path = video_save_path+'/'+video_filename
    audio_path = gen_audio_path(video_filename, audio_dir_path)
    
    #extract audio and save to aduio_path
    print("extract audio file..")
    extract_audio_from_video(video_path, audio_path)
    
    #call whisper to generate transcript
    print("transcribing...")
    result = whisper_model.transcribe(audio_path)
    transcript = result["text"]

    #construct output jsion

    output_json = {
        "video_file_path": video_path,
        "audio_file_path": audio_path,
        "transcript": transcript
    }
    
    return output_json


if __name__ == '__main__':
    app.run(debug=True)

