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
function runPrediction(){
  var dataset = $('#evaluate-dataset').val();
  if (dataset=='custom'){
    if($('#prediction-file')[0].files.length==0){
      alert('need to upload file before running prediction!');
      return false;
    }
  }
  return true;
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
    var action = $(document.activeElement).val();
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
      $('#msg_content').text('one training history deleted.');
      $('#action_msg').fadeIn().delay(3000).fadeOut(1000);
    } else if ($(document.activeElement).val()=='restore'){
      e.preventDefault();
      $.post($(this).attr('action'), $(this).serialize()+'&action=restore', function(data){
      });
      $('#msg_content').text('neural network structure restored');
      $('#action_msg').fadeIn().delay(2000).fadeOut(1000);
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
