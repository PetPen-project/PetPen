$(function(){
	var w = $("#mwt_slider_content").width();
	$('#mwt_slider_content').css('height', ($(window).height() - 20) + 'px' ); //將區塊自動撐滿畫面高度
	
	$("#mwt_tab").click(function(){ //滑鼠滑入時
		if ($("#mwt_mwt_slider_scroll").css('left') == '-'+w+'px')
		{
			$("#mwt_mwt_slider_scroll").animate({ left:'0px' }, 600 ,'swing');
		}
	});
	
	
	$("#mwt_slider_content").mouseleave(function(){　//滑鼠離開後
		$("#mwt_mwt_slider_scroll").animate( { left:'-'+w+'px' }, 600 ,'swing');
	});
});
