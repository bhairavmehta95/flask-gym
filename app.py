#!/usr/bin/env python                                                                                                                                                                          
# -*- coding: utf-8 -*-                                                                                                                                                                        

from flask import Flask, stream_with_context, request, Response, flash                                                                                                                         
from time import sleep 

import gym 
import numpy as np
from PIL import Image
import io                                                                                                                                             

app = Flask(__name__)                                                                                                                                                                          

def stream_template(template_name, **context):                                                                                                                                                 
    app.update_template_context(context)                                                                                                                                                       
    t = app.jinja_env.get_template(template_name)                                                                                                                                              
    rv = t.stream(context)                                                                                                                                                                     
    rv.disable_buffering()                                                                                                                                                                     
    return rv                                                                                                                                                                                  

env = gym.make('LunarLander-v2')
env.reset()

def generate():  
    d = False
    env.reset()
    while True:                                                                                                                                   
        _, _, d, _ = env.step(env.action_space.sample())
        
        img = env.render(mode='rgb_array') 
        im = np.flip(img.transpose((0, 1, 2)), 1)

        # convert numpy array to PIL Image
        img = Image.fromarray(im.astype('uint8'))

        # create file-object in memory
        file_object = io.BytesIO()
        img.save(file_object, format='PNG')
        file_object = file_object.getvalue()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + file_object + b'\r\n')

        if d: env.reset()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')                                                                                                                                                                          
def stream_view():                                                                                                                                                                             
    rows = generate()                                                                                                                                                                          
    return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")                                                                                                                              

if __name__ == '__main__':                                                                                                                                                                     
    app.debug = True                                                                                                                                                                           
    app.run()   