//time
var waitMS = 300;
var limitMS = 60000;

//timer
var timerProgress;//request from server (python)
var idleTime = 0;//file not update in time

//keywords
var wordForTraining = "training model";
var wordForIdle = "system idle"
var wordForTesting = "start testing";
var wordForLoading = "loading model structure";
var wordForError = "error found";
var wordForFinish = "finish training"
var stopKeyword = "job done";//finish training

//variable
var currentMode = "idle";
var svg = '';
var chart = '';

$(function(){
  $('#trainModel').click(function(){
    $.ajax({
      async:false,
      url: "/model/api/backend/",
      method:"POST",
      data:{
        command: "train",
        name: $('#expName').val(),
        project: project_id
      }
    });
    $('#trainModel').attr('disabled',true);
    currentMode = "loading";
  });
  $('#stopTrainModel').click(function(){
    $.ajax({
      async:false,
      url: "/model/api/backend/",
      method:"POST",
      data:{
        command: "stop",
        project: project_id
      }
    });
  });
  initPlot();
  initJsonPython();//init

  timerProgress = setInterval(function () {//timer
    loadJsonPython();
  }, waitMS);
  $(this).mousedown(function(){
    idleTime = 0;
  });
  $(this).keypress(function(){
    idleTime = 0;
  });
});
function getStatus(data){
  switch(data['status']){
    case wordForIdle: currentMode = 'idle'; break;
    case wordForTraining: currentMode = 'training'; break;
    case wordForLoading: currentMode = 'loading'; emptyPlotCode(); break;
    case wordForError: currentMode = 'error'; break;
    case wordForFinish: currentMode = 'finish'; break;
  }
  return currentMode;
};
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
function printJSON(data){
  //===== switch mode =====//
  currentMode = getStatus(data);
//update data
  if(JSON.stringify(data)){
    //===== updated data on screen =====//
    $('#txfStatus').val(data['status']);//status
    $('#txfTime').val(data['time']);//time
    if ('loss' in data && data['loss']['value']!='null'){
      var lossText = data['loss']['type'] + ': ' + data['loss']['value'];//loss
    } else{
      var lossText = '--';
    }
    if(currentMode=='training'){
      $('.txfLoss[name="' + currentMode + '"]').val(lossText);
      setProgessBar('barEpoch', currentMode, data['epoch']);//epoch
      setProgessBar('barProgress', currentMode, data['progress']);//progress
    }else if(currentMode=='error'){
      $('#txfError').val(data['detail']);
    }
  }

    //different mode
    switch(currentMode){
      case 'training':
        $('#trainingDiv').show();
        $('#loadingDiv,#testingDiv,#errorDiv').hide();
        $('#stopTrainModel').attr('disabled',false);
        $('#trainModel').attr('disabled',true);
        break;
      case 'error':
        $('#errorDiv').show();
        $('#loadingDiv,trainingDiv').hide();
        $('#trainModel').attr('disabled',false);
        $('#stopTrainModel').attr('disabled',true);
        break;
      case 'loading':
        $('#loadingDiv').show();
        $('#trainingDiv,#errorDiv').hide();
        $('#trainModel').attr('disabled',true);
        $('#stopTrainModel').attr('disabled',false);
        break;
      case 'finish':
        $('#trainingDiv').show();
        $('#loadingDiv,#testingDiv,#errorDiv').hide();
        $('#trainModel').attr('disabled',false);
        $('#stopTrainModel').attr('disabled',true);
        break;
      default:
        $('#trainingDiv,#loadingDiv,#errorDiv').hide();
        $('#trainModel').attr('disabled',false);
        $('#stopTrainModel').attr('disabled',true);
        break;
    }
};
function initPlot(){
  svg = d3.select("svg");
  chart = nv.models.lineChart()
    .x(function(d,i){return d[0]})
    .y(function(d){return d[1]})
    .color(d3.scale.category10().range())
    .useInteractiveGuideline(true)
    .noData('Empty data')
    ;
  chart.xAxis
    .axisLabel('Epoch');
  chart.yAxis
    .tickFormat(d3.format(',.3f'));
  nv.utils.windowResize(chart.update);

  svg.datum([])
    .call(chart);
  return chart;
};
function updatePlot(data){
  plotdata = svg.datum();
  if(data.status==wordForTraining && typeof(data.loss.value)=='number'){
    if (!plotdata[0]){
      plotdata[0] = {'key':'training','values':[[data.epoch[0],data.loss.value]]};
    }else{
      if(!plotdata[0].values.find(function(item,index,array){
        return item[0] == data.epoch[0];
      })){
        plotdata[0].values.push([data.epoch[0],data.loss.value]);
      }
    }
  }
  //chart.yDomain = [-1,10];//[plotdata[0].values]
  //plotdata.push({'key':'test','values':[[data.loss.value]]});
  //console.log(plotdata);
  svg.call(chart);
  //chart.update();
};
function emptyPlotCode(data){
  ;
};
function setProgessBar(barClass, barName, dataArray){
  if(barName != 'training' && barName != 'testing')
    return;
  var num1 = 0, num2 = 0;
  if(dataArray.length > 0) num1 = dataArray[0];
  if(dataArray.length > 1) num2 = dataArray[1];
  progressBar($('.' + barClass + '[name="' + barName + '"]'), num1, num2, num1 + "/" + num2);
};
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
};
//call when error
function errorJSON(data){
  if(typeof data != 'undefined'){
    console.log(data['responseText']);
  }
  else{
    console.log('undefined error found');
    console.log(data);
  }
};
function loadJsonPython(){
  idleTime = idleTime + waitMS;
  if (currentMode!='error' && currentMode!='finish' && (idleTime < limitMS || currentMode=='training')){
    $.ajax({
      async: false,
      dataType: "json",
      type: 'POST',
      url: "/model/api/parse/",
      data: {
        project_id: project_id
      },
      success: function(data){
        printJSON(data);
        updatePlot(data);
      },
      error: function(err){
        console.log('error loading json from api');
        console.log(err);
      } // pass
      //error: errorJSON
    });
  }
};

