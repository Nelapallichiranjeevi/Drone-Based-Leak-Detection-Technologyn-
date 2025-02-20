from flask import Flask, Response, jsonify, render_template
import cv2
import random
import time

app = Flask(__name__)
camera = cv2.VideoCapture(0)
stop_video = False  # Flag to stop video manually

def generate_frames():
    global stop_video
    while True:
        if stop_video:
            print("Video feed manually stopped.")
            break
        
        success, frame = camera.read()
        if not success:
            print("Failed to capture frame")
            break
        
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    global stop_video
    stop_video = False  # Reset flag when starting
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/analyze_frame')
def analyze_frame():
    success, frame = camera.read()
    if not success:
        return jsonify({"error": "Frame capture failed"})
    
    leak_probability = round(random.uniform(0.1, 0.9), 2)
    result = "Leak Detected!" if leak_probability > 0.5 else "No Leak"
    return jsonify({"leak_probability": leak_probability, "result": result})

@app.route('/stop_video', methods=['POST'])
def stop_video_feed():
    global stop_video
    stop_video = True
    return jsonify({"message": "Video feed stopped manually"})

@app.route('/start_video', methods=['POST'])
def start_video_feed():
    global stop_video
    stop_video = False
    return jsonify({"message": "Video feed started"})

if __name__ == '__main__':
    app.run(debug=True)