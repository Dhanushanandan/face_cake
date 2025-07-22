from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import os
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
UPPER_LIP = 13
LOWER_LIP = 14

current_status = "Waiting..."
face_captured = False
mouth_captured = False
email_sent = False  # Ensures one email per session

def send_email_auto():
    try:
        sender_email = 'danushanandan1@gmail.com'  # replace
        app_password = 'rxux flxs utqi gola'     # replace
        receiver_email = 'danushanandan1@gmail.com'  # replace

        subject = "🎉 Happy Birthday from Adhira!"
        body = "Here are your celebration photos!"

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg.set_content(body)

        # Attach both images if they exist
        if os.path.exists("static/face_detected.jpg"):
            with open('static/face_detected.jpg', 'rb') as f:
                msg.add_attachment(f.read(), maintype='image', subtype='jpeg', filename='face_detected.jpg')
        if os.path.exists("static/mouth_open.jpg"):
            with open('static/mouth_open.jpg', 'rb') as f:
                msg.add_attachment(f.read(), maintype='image', subtype='jpeg', filename='mouth_open.jpg')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(msg)

        print("✅ Email sent successfully!")

    except Exception as e:
        print("❌ Email sending failed:", e)

def detect_mouth():
    global current_status, face_captured, mouth_captured, email_sent

    # Reset everything on page refresh
    face_captured = False
    mouth_captured = False
    email_sent = False

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
            msg = "Face Detected"

            if not face_captured:
                cv2.imwrite("static/face_detected.jpg", frame)
                print("📸 Face detected image saved!")
                face_captured = True

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
                    if not mouth_captured:
                        cv2.imwrite("static/mouth_open.jpg", frame)
                        print("📸 Mouth open image saved!")
                        mouth_captured = True

                # Send email once both captured
                if face_captured and mouth_captured and not email_sent:
                    send_email_auto()
                    email_sent = True

                cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

        current_status = msg

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
