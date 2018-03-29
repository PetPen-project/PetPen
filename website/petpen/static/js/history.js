function reloadHistory(data){
  $('#history-detail').html($(data).find('#history-detail').children());
};
function setDataset(dataset){
  $('input[name=dataset]').val($('#evaluate-dataset').val());
  if ($('#evaluate-dataset').val()=='custom'){
    $('#pred-label').removeClass('disabled');
    $('#prediction-file').attr('disabled',false);
  }
  else if($('#evaluate-dataset').val()=='test'){
    $('#pred-label').addClass('disabled');
    $('#prediction-file').attr('disabled',true);
  }
};
function runEvaluation(project_id){
  //$.ajax({
    //async: false,
    //type: 'post',
    //url: '/model/api/backend/',
    //data:{
      //csrfmiddlewaretoken: window.CSRF_TOKEN,
      //command: 'evaluate',
      //dataset: '',
      //project: project_id
    //}
  //});
};
$(function(){
  $("a[id^='loadHistory']").on('click',function(){
    var link = $(this);
    console.log(window.location.pathname);
    $.ajax({
      type: 'post',
      url: window.location.pathname,
      data: {
        history: link[0].dataset['history'],
        csrfmiddlewaretoken: window.CSRF_TOKEN
      },
      success: function(data){reloadHistory(data);},
      error: function(xhr,status,error){
        alert(error);
      }
    });
  });
  $("form[name=historyActionForm]").submit(function(e){
    if ($(document.activeElement).val()=='delete'){
      e.preventDefault();
      $.post($(this).attr('action'), $(this).serialize()+'&action=delete', function(data){
        console.log($(':focus').parents('.item')[0]);
        $(':focus').parents('.item')[0].remove();
        //$('#history-detail').html($(data).find('#history-detail').children());
        reloadHistory(data);
        <!--location.reload();-->
        <!--$(document).html($(data));-->
      }).fail(function(data){alert(data);
      });
    }
  });

  //$('#deleteAction').click(function(){
    //$('a[id^="loadHistory"]').prepend('<input type="checkbox" name="checkDelete" value="delete" class="mr-2 my-auto">');
    //$(document).mouseup(function(e){
      //var container = $('#sidebar');
      //if (!container.is(e.target) && container.has(e.target).length === 0)
      //{
        //$('input[name=checkDelete]').remove();
      //}
    //});
  //});
});
