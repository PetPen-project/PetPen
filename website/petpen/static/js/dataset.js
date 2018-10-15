$(document).ready(function(){
  var modal = $("#dataset-modal");
  $(".filetype-badge").each(function(){
    if ($(this).text() == 'csv'){
      $(this).css("background","#FFCC00");
    } else if($(this).text() == 'pickle'){
      $(this).css("background","#0033CC");
    } else if($(this).text() == 'npy'){
      $(this).css("background","#EF1C7B");
    }
  });
  $('.error-message .close').click(function(){
    $('.error-message').empty();
    $('.error-message').hide();
  });
  $("#open-modal").click(function(){
    modal.show();
    $(document).mouseup(function(e){
      var container = $(".form-content");
      if (!container.is(e.target) && container.has(e.target).length === 0){
        modal.hide();
      }
    });
  });
  $("#close-modal").click(function(){
    modal.hide();
  });
  $("a[name=dataset-link]").click(function(){
    $(".dataset-loading").show();
  });
  $("#info-sidebar .close").click(function(){
    $("#info-sidebar").css("width","0");
  });
  $('#dataUploadForm').submit(function(e){
    e.preventDefault();
    $('.barProgress').css('width', '0%');
    $('#percent').text('0%');
    var data = new FormData($('#dataUploadForm')[0]);
    $('#percent').on('DOMSubtreeModified',function(){
      if ($('#percent').text()=='100%'){
        $('#upload-progress').css('display','none');
        $('#dataset-processing').css('display','block');
      }
    });
    $.ajax({
      processData: false,
      contentType: false,
      data: data,
      type: $('#dataUploadForm').attr('method'),
      url: $('#dataUploadForm').attr('action'),
      xhr: function(){
        $('#upload-progress').css('display','block');
        $('#percent').text('0%');
        var xhr = new window.XMLHttpRequest();
        xhr.upload.addEventListener("progress", function(e){
          if (e.lengthComputable) {
            var percentComplete = e.loaded / e.total;
            $('.barProgress').css('width', (percentComplete)*100+'%');
            $('#percent').text(Math.floor((percentComplete)*100)+'%');
          }
        }, false);
        return xhr;
      },
      success: function(response){
        //$('.dataset-container').html($(response).find('.dataset-container'));
        //$('#dataset-processing').css('display','none');
        window.location.href = window.location.href;
      },
      error: function(response){
        alert(response['message']);
      }
    });
  });
  $('select[name=input-type]').change(function(){
    if ($('select[name=input-type]').val()=='numeric'){
      $('#testing-input-n').show();
      $('input#id-testing-input-file').prop('required',true);
      $('#testing-input-i').hide();
      $('input#id-testing-input-img').prop('required',false);
      $('#training-input-n').show();
      $('input#id-training-input-file').prop('required',true);
      $('#training-input-i').hide();
      $('input#id-training-input-img').prop('required',false);
    } else if ($('select[name=input-type]').val()=='image'){
      $('#testing-input-n').hide();
      $('input#id-testing-input-file').prop('required',false);
      $('#testing-input-i').show();
      $('input#id-testing-input-img').prop('required',true);
      $('#training-input-n').hide();
      $('input#id-training-input-file').prop('required',false);
      $('#training-input-i').show();
      $('input#id-training-input-img').prop('required',true);
    }
  });
  $('select[name=output-type]').change(function(){
    if ($('select[name=output-type]').val()=='numeric'){ 
      $('#testing-output-n').show();
      $('input#id-testing-output-file').prop('required',true);
      $('#testing-output-i').hide();
      $('input#id-testing-output-img').prop('required',false);
      $('#training-output-n').show();
      $('input#id-training-output-file').prop('required',true);
      $('#training-output-i').hide();
      $('input#id-training-output-img').prop('required',false);
    } else if ($('select[name=output-type]').val()=='image'){
      $('#testing-output-n').hide();
      $('input#id-testing-output-file').prop('required',false);
      $('#testing-output-i').show();
      $('input#id-testing-output-img').prop('required',true);
      $('#training-output-n').hide();
      $('input#id-training-output-file').prop('required',false);
      $('#training-output-i').show();
      $('input#id-training-output-img').prop('required',true);
    }
  });
});

function setDeleteId(text){
  $("#delete-id").val(text);
};
