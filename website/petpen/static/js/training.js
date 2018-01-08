//time
var waitMS = 300;
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
  //$('#errorDiv,#loadingDiv,#trainingDiv').hide();
	initJsonPython();//init
	
  timerProgress = setInterval(function () {//timer
    loadJsonPython();
  }, waitMS);
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
    error: errorJSON
  });
};
//call when success
function printJSON(data){
  //alert(JSON.stringify(data));//print json
  
  //===== switch mode =====//
  switch(data['status']){
    case 'system idle': currentMode = 'idle'; break;
    case wordToTraining: currentMode = 'training'; break;
    case wordToTesting: currentMode = 'testing'; break;
    case wordToLoading: currentMode = 'loading'; emptyPlotCode(); break;
    case 'error': currentMode = 'error'; break;
    case 'finish training': loadHTMLPython(); break;
  }
  
  //update data
  //if(JSON.stringify(savedJSON) != JSON.stringify(data)){
  if(JSON.stringify(data)){
    savedJSON = data;//update
    lastUpdateTimestamp = new Date().getTime();//time
    
    //===== updated data on screen =====//
    $('#txfStatus').val(data['status']);//status
    $('#txfTime').val(data['time']);//time
    if (data['status']=='error'){$('#txfError').val(data['detail']);}
    if ('loss' in data && data['loss']['value']!='null'){
      var lossText = data['loss']['type'] + ':' + data['loss']['value'];//loss
    } else{
      var lossText = '--';
    }
    $('.txfLoss[name="' + currentMode + '"]').val(lossText);
    setProgessBar('barEpoch', currentMode, data['epoch']);//epoch
    setProgessBar('barProgress', currentMode, data['progress']);//progress

    //different mode
    switch(currentMode){
      case 'training':
        $('#trainingDiv').show();
        $('#loadingDiv,#testingDiv,#errorDiv').hide();
        break;
      //case 'testing':
        //$('#trainingDiv,#testingDiv').show();
        //$('#loadingDiv').hide();
        //break;
      case 'error':
        $('#errorDiv').show();
        $('#loadingDiv,trainingDiv').hide();
        break;
      case 'loading':
        $('#loadingDiv').show();
        $('#trainingDiv,#errorDiv').hide();
        break;
      default:
        $('#trainingDiv,#loadingDiv,#errorDiv').hide();
        break;
    }

    //===== finish =====//
    if(data['status'] == stopKeyword) stopTimer();//stop
  }
};
function emptyPlotCode(){
  ;
}
function setProgessBar(barClass, barName, dataArray){
  if(barName != 'training' && barName != 'testing')
    return;
  var num1 = 0, num2 = 0;
  if(dataArray.length > 0) num1 = dataArray[0];
  if(dataArray.length > 1) num2 = dataArray[1];
  progressBar($('.' + barClass + '[name="' + barName + '"]'), num1, num2, num1 + "/" + num2);
}
//progress animation bar
function progressBar($bar, count, total, text) {
  var percentage = 100;
  if(total != 0) {
    percentage = parseInt(parseInt(count) * 100 / total);
    if (percentage > 100) percentage = 100;
    $bar.width(parseInt(percentage) + "%");

    var barText = percentage + "%";
    if (text != "") barText = text + " - " + barText;
    $bar.text(barText);
  } else {
    $bar.width(parseInt(percentage) + "%");//width of bar
    $bar.text("Data Not Load");//text of bar
  }
  
  if (percentage >= 100) $($bar).removeClass('active');
  else $($bar).addClass('active');	
}
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
    error: function(){;} // pass
    //error: errorJSON
  });
};

