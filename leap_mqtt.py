import leap
import time
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, respons_code):
    print('MQTT Connected:status {0}'.format(respons_code))
#    client.subscribe('leapmotion')

def on_message(client, userdata, msg):
    print(msg.topic + ' ' + str(msg.payload))


def init_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect('192.168.1.148', 1883, 60)
    client.loop_start()
    return client

class TrackingListener(leap.Listener):
    def __init__(self,mq_client):
        super(TrackingListener, self).__init__()
        self.mq_client = mq_client

    def on_connection_event(self, event):
        print("LeapMotion2 Connected!", event)

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()
        print(f"LeapMotion2 Found device {info.serial}")
       
    def on_tracking_event(self, event):
        # 定期的に情報表示
        if event.tracking_frame_id %200 ==0:
            print("Trk",event.tracking_frame_id, len(event.hands))
        if len(event.hands)==0:
            return

        hand = event.hands[0]        
        if hand.type != leap.HandType.Right:
            print("Left hand is not supported")
            return
        position = hand.palm.position
        orientation = hand.palm.orientation
        pinch = hand.pinch_strength
        grab = hand.grab_strength

        sd = {
            "pos":{
                "x":position[0],
                "y":position[1],
                "z":position[2]
            },
            "ori":{
                "x":orientation[0],
                "y":orientation[1],
                "z":orientation[2],
                "w":orientation[3]
            },
            "pinch":pinch,
            "grab":grab            
        }
        print(sd)
        st = json.dumps(sd)
        self.mq_client.publish('dev/leap',st)

        

        #オリエンテーションをどう計算するか？


        
        # とりあえず、そのまま送ってみよう






def main():
    mq_client = init_mqtt()

    tracking_listener = TrackingListener(mq_client)

    connection = leap.Connection()
    connection.add_listener(tracking_listener)

    print("Run!")

    running = True

    with connection.open():
        connection.set_tracking_mode(leap.TrackingMode.Desktop)
#        canvas.set_tracking_mode(leap.TrackingMode.Desktop)
        while running:
            time.sleep(1)
            pass


if __name__ == "__main__":
    main()
