module.exports = function(RED) {
    function wago(config) {
        RED.nodes.createNode(this,config);
        var context = this.context();
        var node = this;
        this.on('input', function(msg) {

        var mbOutData = {payload: [0,0,0,0]};
        var mbInData = msg;
        
        var diagMsg = "Im Waiting";
        
        var statusColor;
        
        var getDataState = context.get('getDataState')||1;
        
        var voltsHold = [];
        var voltsL1 = context.get('voltsL1')||0;
        var voltsL2 = context.get('voltsL2')||0;
        var voltsL3 = context.get('voltsL3')||0;
        
        var ampresHold = [];
        var ampresL1 = context.get('ampresL1')||0;
        var ampresL2 = context.get('ampresL2')||0;
        var ampresL3 = context.get('ampresL3')||0;
        
        var freqHold = [];
        var freqL1 = context.get('freqL1')||0;
        var freqL2 = context.get('freqL2')||0;
        var freqL3 = context.get('freqL3')||0;
        
        
        mbOutData.payload[0] = "0";      // no reg comms and L1 measure
        mbOutData.payload[1] = "2304";   // AC line measurement
            
            switch(getDataState)    {
                case 1: //voltage
                mbOutData.payload[2] = "1284";   // requests volts for L1 and L2
                mbOutData.payload[3] = "6";      // requests volts for L3 
                statusColor = "red";
                break;
                case 2: // current 
                mbOutData.payload[2] = "513";   // requests ampres for L1 and L2
                mbOutData.payload[3] = "3" ;     // requests ampres for L3     
                statusColor = "yellow";
                break;
                case 3: //frequency
                mbOutData.payload[2] = "4368";   // requests frequency for L1 and L2
                mbOutData.payload[3] = "18" ;     // requests frequency for L3     
                statusColor = "green";
                break;
                case 4: // wattage
                break;
            }
            // voltage
            if ((mbInData.payload[2] == "1284") && (mbInData.payload[3] == "6"))  {
                diagMsg = {payload: "getting voltage"};
                voltsHold[0] = parseInt(mbInData.payload[4] + (mbInData.payload[5] << 8));
                voltsHold[1] = parseInt(mbInData.payload[6] + (mbInData.payload[7] << 8));
                voltsHold[2] = parseInt(mbInData.payload[8] + (mbInData.payload[9] << 8));
                voltsL1 = {payload: voltsHold[0].toString() / 100};
                voltsL2 = {payload: voltsHold[1].toString() / 100};
                voltsL3 = {payload: voltsHold[2].toString() / 100};
                context.set('voltsL1', voltsL1);
                context.set('voltsL2', voltsL2);
                context.set('voltsL3', voltsL3);
                getDataState = 2;
            }
            // current 
            if ((mbInData.payload[2] == "513") && (mbInData.payload[3] == "3"))  {
                diagMsg = {payload: "getting current"};
                ampresHold[0] = parseInt(mbInData.payload[4] + (mbInData.payload[5] << 8));
                ampresHold[1] = parseInt(mbInData.payload[6] + (mbInData.payload[7] << 8));
                ampresHold[2] = parseInt(mbInData.payload[8] + (mbInData.payload[9] << 8));
                ampresL1 = {payload: ampresHold[0].toString() / 1000};
                ampresL2 = {payload: ampresHold[1].toString() / 1000};
                ampresL3 = {payload: ampresHold[2].toString() / 1000};
                context.set('ampresL1', ampresL1);
                context.set('ampresL2', ampresL2);
                context.set('ampresL3', ampresL3);
                getDataState = 3;
            }
            // frequency
            if ((mbInData.payload[2] == "4368") && (mbInData.payload[3] == "18"))  {
                diagMsg = {payload: "getting frequency"};
                freqHold[0] = parseInt(mbInData.payload[4] + (mbInData.payload[5] << 8));
                freqHold[1] = parseInt(mbInData.payload[6] + (mbInData.payload[7] << 8));
                freqHold[2] = parseInt(mbInData.payload[8] + (mbInData.payload[9] << 8));
                freqL1 = {payload: freqHold[0].toString() / 1000};
                freqL2 = {payload: freqHold[1].toString() / 1000};
                freqL3 = {payload: freqHold[2].toString() / 1000};
                context.set('freqL1', freqL1);
                context.set('freqL2', freqL2);
                context.set('freqL3', freqL3);
                getDataState = 1;
    }
        node.status({fill: statusColor,shape: "ring",text: diagMsg.payload});
        context.set('getDataState', getDataState);
        node.send([diagMsg, mbOutData, voltsL1, voltsL2, voltsL3, ampresL1, ampresL2, ampresL3, freqL1, freqL2, freqL3]);
        
        });
    }
    RED.nodes.registerType("Power Meas.",wago);
};
