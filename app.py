from flask import Flask, render_template, Response
import ffmpeg

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    video_path = 'path_to_your_video.mp4'
    return Response(generate(video_path), mimetype='video/mp4')

def generate(video_path):
    # Open video file
    probe = ffmpeg.probe(video_path)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])

    process = (
        ffmpeg
        .input(video_path)
        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
        .run_async(pipe_stdout=True)
    )

    while True:
        in_bytes = process.stdout.read(width * height * 3)
        if not in_bytes:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + in_bytes + b'\r\n')

    process.stdout.close()
    process.wait()
if __name__ == '__main__':
    app.run(debug=True)
