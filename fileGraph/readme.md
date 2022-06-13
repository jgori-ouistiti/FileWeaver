## fileGraph

### First time: install node modules

A: `% npm install`

Or 

B: npm install -D nw@0.65.0-sdk

### Test with simulation

Assuming `nw` is on the PATH:

A: `% nw .`

B: `% npm start`

This will start nwjs and open an empty window. 


In a different terminal:

```
% cd test  
% node sim.js
```

This will send the content of `test/exchange-log.json` to the viewer. The graph should animate.

### Run for real

In `index.js`, comment/uncomment lines 173/174 to point to the "real" `exchange.json`
