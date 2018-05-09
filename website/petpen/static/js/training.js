//time
var waitMS = 300;
var limitMS = 60000;

//timer
var timerProgress;//request from server (python)
var idleTime = 0;//file not update in time

//keywords
var wordToTraining = "start training model";
var wordToTesting = "start testing";
var wordToLoading = "loading model";
var stopKeyword = "job done";//finish training

//variable
var savedJSON = {};
var currentMode = "idle";
var lastUpdateTimestamp = 0;
var svg = '';
var chart = '';

$(function(){
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
    case 'finish training': break;
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
function enableStopBtn(){
  ;
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
//function initPlot(width,height,margin){
  //margin = margin || {
    //top: 30,
    //right: 20,
    //bottom: 40,
    //left: 50
  //};
  //width = width - margin.left - margin.right;
  //height = height - margin.top - margin.bottom;

  //var y = d3.scaleLinear().range([height, 0]);
  //var x = d3.scaleLinear().range([0, width]);

    //svg = svg.attr("width", width + margin.left + margin.right)
    //.attr("height", height + margin.top + margin.bottom)
    //.append("g")
    //.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  //// Scale the range of the data
  //x.domain([0, 10]);
  //y.domain([0.0, 1.0]);

  //var xAxis = d3.axisBottom(x).ticks(5);

  //var yAxis = d3.axisLeft(y).ticks(5);
  //data = [
    //{"x":1, "y":0.4},
    //{"x":3, "y":0.2},
    //{"x":5, "y":0.7},
    //{"x":7, "y":0.5},
    //{"x":9, "y":0.8}
  //];
  //line = d3.line()
    //.x(function(d){return x(d.x);})
    //.y(function(d){return y(d.y);});
  //svg.append("path")
    //.attr("d",line(data))
    //.attr("stroke","blue")
    //.attr("stroke-width",2)
    //.attr("fill","none");

  //svg.append("g") // Add the X Axis
    //.attr("transform", "translate(0," + height + ")")
    //.call(xAxis);
  //svg.append("g") // Add the Y Axis
    //.call(yAxis);
  
  //svg.append("text") // Add the X label
    //.attr("x",(width/2))
    //.attr("y",height+(margin.top))
    //.text("Epoch");
  //svg.append("text") // Add the Y label
    //.attr("transform","rotate(90)")
    //.attr("dy","2.5rem")
    //.text("Loss");
//}
function updatePlot(data){
  //console.log(data.epoch[0]);
  plotdata = svg.datum();
  if(data.status=='start training model'){
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
    alert(data['responseText']);
    //stopTimer();//stop
  }
  else{
  alert('undefined error found');
  alert(data);
  }
};
function loadJsonPython(){
  idleTime = idleTime + waitMS;
  if (idleTime < limitMS && currentMode=='training'){
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
      error: function(){console.log('error loading json from api');} // pass
      //error: errorJSON
    });
  }
};

