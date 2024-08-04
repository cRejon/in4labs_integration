FROM nodered/node-red:4.0.2-22

RUN rm /usr/src/node-red/node_modules/@node-red/editor-client/public/red/red.js 
RUN rm /usr/src/node-red/node_modules/@node-red/editor-client/public/red/red.min.js

COPY ./red.js /usr/src/node-red/node_modules/@node-red/editor-client/public/red
COPY ./red.min.js /usr/src/node-red/node_modules/@node-red/editor-client/public/red

RUN rm /data/flows.json 
COPY ./flows.json /data