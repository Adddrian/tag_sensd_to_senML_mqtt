#------------------------------------------------#
#                  Tag to mqtt                   #
#                                                #
#                                                #
#  Created by Adrian Gortzak and Jimmy fjallid   #
#------------------------------------------------#

import socket, select, string, sys, re
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import json

#-- config -----------
mqtt_host = "test.mqtt.com"
mqtt_port = 1883
mqtt_username = "test"
mqtt_password = "test"
mqtt_client_name = "testClient-1234"

host="example.com"
port=1234
location="africa"
organisation="kth"
sensorName="sensor"
#---------------------

def my_publish(topic, message):
    publish.single(topic, payload=message, qos=0, retain=False, hostname=mqtt_host, port=mqtt_port, client_id=mqtt_client_name, keepalive=60, will=None, auth= {'username':mqtt_username, 'password':mqtt_password}, tls=None, 
protocol=mqtt.MQTTv31)

#main function
if __name__ == "__main__":
    regex = "([0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})(?: TZ=([A-Z]{2,5}))(?: UT=([0-9]{10,}))(?: GW_LAT=([-?\d+]{1,3}.[0-9]{0,5}))(?: GW_LON=([-?\d+]{1,3}.[0-9]{0,5}))(?:\s*.+)(?:\s*TXT=([a-zA-Z0-9-]*))(?:\s+E64=([a-fA-F0-9]{6,}))?(?:\s+PS=[0,1])?(?:\s+(?:T|T_[A-Z0-9]+)=([0-9\.]{2,6}))?(?:(?:\s*V_[A-Z0-9]{1,4}=[0-9.]{1,4})+)?(?:\s+T_[A-Z0-9]+=([0-9.]{1,6}))?(?:\s+RH_[A-Z0-9]{1,6}=([0-9.]{1,5}))?\s+(?:.*)(?:\[.*])"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print ('Unable to connect')
        sys.exit()

    print ('Connected to remote host')

    while 1:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])

        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print ('Connection closed')
                    sys.exit()
                else :
                    #print data
                    m = re.search(regex, str(data))
                    response = []
                    hasSupportedData = 0
                    topic = 'greeniot/'+location+'/'+organisation+'/'+sensorName+'/'
                    if m.group(7): #there is some nodes without id  that publish sensor data
                        topic = topic + str(m.group(7))
                        node  = {'bt':m.group(3),'bn':m.group(7), 'lat':m.group(4),'long':m.group(5)}
                        response.append(node)
                        if m.group(9):
                            response.append({'v':m.group(9), 'n':"temperature"})
                            hasSupportedData = 1
                        elif m.group(8):
                            response.append({'v':m.group(8), 'n':"temperature"})
                            hasSupportedData = 1
                        if m.group(10):
                            response.append({'v':m.group(10), 'n':"humidity"})
                            hasSupportedData = 1
                        if hasSupportedData:
                            print (topic)
                            print (response)
                            my_publish(topic+'/sensors',str(json.dumps(response)))
                    else:
                        print (str(data))
