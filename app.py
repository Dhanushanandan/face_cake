from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import math
import os

app = Flask(__name__)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
UPPER_LIP = 13
LOWER_LIP = 14

current_status = "Waiting..."

def detect_mouth():
    global current_status
    cap = cv2.VideoCapture(0)

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        msg = "Face not detected"

        if results.multi_face_landmarks:
            for face in results.multi_face_landmarks:
                upper = face.landmark[UPPER_LIP]
                lower = face.landmark[LOWER_LIP]
                h, w, _ = frame.shape

                upper_y = int(upper.y * h)
                lower_y = int(lower.y * h)
                mouth_open_dist = abs(lower_y - upper_y)

                cx = int((upper.x + lower.x) / 2 * w)
                cy = int((upper.y + lower.y) / 2 * h)

                if mouth_open_dist > 15:
                    msg = "Mouth Open"
                else:
                    msg = "Happy Birthday ADHIRA!"

                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

        current_status = msg

        # cv2.putText(frame, msg, (30, 60), cv2.FONT_HERSHEY_SIMPLEX,
        #             1.2, (0, 255, 0), 3)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(detect_mouth(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    global current_status
    return jsonify({'message': current_status})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
