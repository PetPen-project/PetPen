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
    var data = new FormData($('#dataUploadForm')[0]);
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
        //Upload progress
        xhr.upload.addEventListener("progress", function(e){
          if (e.lengthComputable) {
            var percentComplete = e.loaded / e.total;
            //Do something with upload progress
            $('.barProgress').css ('width', (percentComplete)*100+'%');
            $('#percent').text(Math.floor((percentComplete)*100)+'%');
          }
        }, false);
        xhr.addEventListener("loadend", function(e){
          $('upload-progress').css('display','none');
          $('dataset-processing').css('display','block');
        }, false);
        return xhr;
      },
      success: function(response){
        location.reload();
      },
      error: function(response){
        alert(response['message']);
      }
    });
  })
});

function setDeleteId(text){
  $("#delete-id").val(text);
};
