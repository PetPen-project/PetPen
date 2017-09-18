var jsonPath = "json/state.json";

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

//veriable
var savedJSON = {};
var currentMode = "idle";
var lastUpdateTimestamp = 0;

//main
$(function(){
	loadJson();//init
	
  loadHTMLPython();

	timerProgress = setInterval(function () {//timer
		loadJson();
	}, waitMS);

	timerLimit = setInterval(function () {//timer
		var currentTime = new Date().getTime();
		//var currentTime = new Date(currentTime);//human format
		//var lastUpdateTime = new Date(lastUpdateTimestamp);//human format
		var interval = new Date(currentTime - lastUpdateTimestamp).getTime();
		if(interval > limitMS){
			$('#textResult').css('color', 'red');//title to red
			stopTimer();//stop
		}
	}, limitMS);

  $('#trainModel').click(function(){
    $.ajax({
      url: "/model/results/",
      method: "GET",
      data:{
        type: "train"
      },
      success: function(){}
    });
  });
});
//==========load json functions==========//
//load json from url
function loadJson(){
	loadJsonPython();
	//loadJsonFile(jsonPath);
};
//load json from python
function loadHTMLPython(){
	$.ajax({
		async: false,
		dataType: "json",
		type: 'GET',
		url: "/model/api/plot/",
		success: parsePlotCode,
		error: function(data){alert(data);}
	});
};

function parsePlotCode(data){
  //alert(JSON.stringify(data));
  $('#div-plot').append($(data['div']));
  $(data['script']).appendTo(document.body);
};

function loadJsonPython(){
	$.ajax({
		async: false,
		dataType: "json",
		type: 'GET',
		url: "/model/api/parse/",
		success: printJSON,
		error: errorJSON
	});
};
//load json from url
function loadJsonUrl(url){
	$.ajax({
		async: false,
		dataType: "json",
		type: 'GET',
		url: url,
		success: printJSON,
		error: errorJSON
	});
}
//load json from file
function loadJsonFile(path){
	$.getJSON(path, function(data) {         
		printJSON(data);
	}).fail( function(d, textStatus, error) {
        alert("getJSON failed, status: " + textStatus + ", error: "+d.responseText);
		stopTimer();//stop
    });
}

//========== progress ==========//
//call when success
function printJSON(data){
	//alert(JSON.stringify(data));//print json
	
	//===== switch mode =====//
	switch(data['status']){
		case wordToTraining: currentMode = 'training'; break;
		case wordToTesting: currentMode = 'testing'; break;
		case wordToLoading: currentMode = 'loading'; break;
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
}

function setProgessBar(barClass, barName, dataArray){
	var num1 = 0, num2 = 0;
	if(dataArray.length > 0) num1 = dataArray[0];
	if(dataArray.length > 1) num2 = dataArray[1];
	progressBar($('.' + barClass + '[name="' + barName + '"]'), num1, num2, num1 + "/" + num2);
}

//call when error
function errorJSON(data){
	if(typeof data != 'undefined'){
		//alert(data['responseText']);
		//stopTimer();//stop
	}
  else{
  alert(data);
  }
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

function stopTimer(){
	//alert('stop');
	$('.progress-bar').removeClass('active');
	//stop
	clearInterval(timerProgress);
	clearInterval(timerLimit);
}
