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
});

function setDeleteId(text){
  $("#delete-id").val(text);
};
