import os
import csv
import json
from flask import Flask, render_template, request, send_file, redirect

app = Flask(__name__)

MAPPER = {
    'angry': 0,
    'sad': 1,
    'happy': 2,
    'calm': 3
}


def get_dataset_path():
    """Get the path of the dataset folder"""
    with open('config.json', 'r') as file:
        config = json.load(file)
    dataset_path = config.get('dataset_path', None)
    if dataset_path is None:
        raise Exception("Config file is corrupted")
    if not os.path.exists(dataset_path):
        raise Exception('Folder {dataset_path} does not exist')
    return dataset_path


def get_index():
    """Get the index of the current video to start annotation with"""
    if os.path.exists('cache/state.json'):
        with open('cache/state.json', 'r') as file:
            state = json.load(file)
        video_index = state.get('index', None)
        if video_index is None:
            raise Exception("State file is corrupted")
        return video_index
    else:
        with open('cache/state.json', 'w') as file:
            json.dump({"index": 0}, file)
        return 0


def save_index(value):
    with open('cache/state.json', 'w') as file:
        json.dump({"index": value}, file)


def get_list_videos():
    dataset_path = get_dataset_path()
    videos = os.scandir(dataset_path)
    videos = list(videos)
    return videos


def save_choice(file_name, emotion):
    with open('cache/annotation.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([file_name, MAPPER[emotion]])


current_video_index = get_index()
videos = get_list_videos()


if current_video_index > len(videos):
    raise Exception('Corrupted state file')


@app.route('/', methods=['GET', 'POST'])
def index():
    global current_video_index

    idx = f'{current_video_index + 1}/{len(videos)}'
    if current_video_index == len(videos):
        # All videos have been shown, redirect to thank you page
        return redirect('/done')

    if request.method == 'POST':
        # Get the user's choice
        choice = request.form['choice']

        # Write choices to a CSV file
        save_choice(videos[current_video_index].name, choice)

        # Move to the next video
        current_video_index = current_video_index + 1

        save_index(current_video_index)

        # Done with annotation
        if current_video_index == len(videos):
            # All videos have been shown, redirect to thank you page
            return redirect('/done')

        idx = f'{current_video_index + 1}/{len(videos)}'

    return render_template(
        'index.html',
        video=videos[current_video_index].path,
        index=idx)


@app.route('/done')
def done():
    return render_template('done.html')


@app.route('/video/<path:video_path>')
def serve_video(video_path):
    return send_file(video_path, mimetype='video/mp4')


if __name__ == '__main__':
    app.run(debug=True)
