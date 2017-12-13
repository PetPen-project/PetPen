//time
var waitMS = 400;
var limitMS = 60000;

//timer
var timerProgress;//request from server (python)
var timerLimit;//file not update in time

//keywords
var wordToTraining = "start training model";
var wordToTesting = "start testing";
var wordToLoading = "loading model";
var stopKeyword = "job done";//finish training

//variable
var savedJSON = {};
var currentMode = "idle";
var lastUpdateTimestamp = 0;

$(function(){
	initJsonPython();//init
	
  //timerProgress = setInterval(function () {//timer
		//loadJsonPython();
	//}, waitMS);
});

function initJsonPython(){
  $.ajax({
    async: false,
    dataType: "json",
    type: 'POST',
    url: "/model/api/parse/",
    data: {type: "init",
      project_id: project_id
    },
    success: printJSON,
    error: function(request, error){
      alert(error);
      alert(arguments);
    }
  });
};
//call when success
function printJSON(data){
  //alert(JSON.stringify(data));//print json
  
  //===== switch mode =====//
  switch(data['status']){
    case wordToTraining: currentMode = 'training'; break;
    case wordToTesting: currentMode = 'testing'; break;
    case wordToLoading: currentMode = 'loading'; emptyPlotCode(); break;
    case 'finish training': loadHTMLPython(); break;
  }
  
  //update data
  if(JSON.stringify(savedJSON) != JSON.stringify(data)){
    savedJSON = data;//update
    lastUpdateTimestamp = new Date().getTime();//time
    
    //===== updated data on screen =====//
    $('#txfStatus').val(data['status']);//status
    $('#txfTime').val(data['time']);//time
    var lossText = data['loss']['type'] + ':' + data['loss']['value'];//loss
    $('.txfLoss[name="' + currentMode + '"]').val(lossText);
    setProgessBar('barEpoch', currentMode, data['epoch']);//epoch
    setProgessBar('barProgress', currentMode, data['progress']);//progress

    //different mode
    switch(currentMode){
      case 'training':
        $('#trainingDiv').show();
        $('#testingDiv,#loadingDiv').hide();
        break;
      case 'testing':
        $('#trainingDiv,#testingDiv').show();
        $('#loadingDiv').hide();
        break;
      case 'loading':
        $('#loadingDiv').show();
        $('#trainingDiv,#testingDiv').hide();
        break;
      default:
        $('#trainingDiv,#testingDiv,#loadingDiv').hide();
        break;
    }

    //===== finish =====//
    if(data['status'] == stopKeyword) stopTimer();//stop
  }
};
//call when error
function errorJSON(data){
  if(typeof data != 'undefined'){
    alert(data['responseText']);
    //stopTimer();//stop
  }
  else{
  alert('undefined error found');
  alert(data);
  }
};
function loadJsonPython(){
  $.ajax({
    async: false,
    dataType: "json",
    type: 'POST',
    url: "/model/api/parse/",
    data: {
      project_id: project_id
    },
    success: printJSON,
    error: errorJSON
  });
};

