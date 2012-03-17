var noAlert = true;
var isOpen  = false;
var timeOut = 12000;
var tID     = '';
var formID  = '';
var isPhone = '';
var shown   = [ ];
var dLong   = 'yyyy-M-d HH:mm:ss';
var dShort  = 'yyyy-M-d';

/* Events */
$('.submit_button').live('click', submitEntryForm);
$('.cancel_button').live('click', cancelForm);
$('.cancel_login').live('click', cancelForm);
$('.edit_entry').live('click', showViewEntry);
$('.view_entry').live('click', showViewEntry);
$('.delete_entry').live('click', deleteEntry);
$('.pay-now').live('click', submitPayPal);
$('.show-candy').live('click', showImage);
$('#close-candy').live('click', closeImage);
$('#new-order').live('click', submitOrder);


/* Binds */
$('body').keyup(cancelOverlay);
$(window).bind('resize',showOverlayBox);

$(document).ready(function() {
    if (window.location.href.indexOf('iphone') > -1) {
        isPhone = 1;
    }
    clearMessage();
    initDatePickers();
});

var toggleContent = function(e) {
    if ($('#details_'+this.id).css('display') == 'none') {
        $('#details_'+this.id).slideDown(300);
    } else {
        $('#details_'+this.id).slideUp(300);
    }
    return false;
};


/* Init Functions */
function initDatePickers() {
    $('#pushupsCreatedDate').datepicker({
        dateFormat: 'yy-mm-dd',
        maxDate: '+0d',
        showButtonPanel: true,
        changeMonth: true,
        changeYear: true
    });
}


/* Overlay Functions */
function clearMessage(out) {
    if (!out) out = timeOut;
    tID = setTimeout(function(){ $('#message').html('') }, out);
}

function showOverlay(overlay) {
    if (tID) clearTimeout(tID);
    if (!overlay) overlay = 'overlay';
    $('#'+overlay).css('display', 'block');
    $('#'+overlay).height($(document).height());
    $('#message').css('color','#000000');
    $('#message').css('margin-left','10px');
    $('#message').css('font-weight','bold');
    $('#message').html('Loading...Please Wait!');
}

function showOverlayBox(overlay, layer) {
    //if box is not set to open then don't do anything
    if (isOpen == false) return;
    // set the properties of the overlay box, the left and top positions
    $(overlay).css({
        display: 'block',
        left: ($('#middle').width() - $(overlay).width())/2,
        top: $(window).scrollTop()+50,
        position: 'absolute'
    });
    // set the window background for the overlay. i.e the body becomes darker
    if (layer) {
        $('.background-cover-top').css({
            display: 'block',
            width: '100%',
            height: $(document).height()
        });
        $(overlay).css({ 'z-index': $(overlay).css('z-index')+layer });
    } else {
        $('.background-cover').css({
            display: 'block',
            width: '100%',
            height: $(document).height()
        });
    }
}

function hideOverlay(overlay, out) {
    if (!overlay) overlay = 'overlay';
    $('#'+overlay).css('display', 'none');
    clearMessage(out);
}

function doOverlayOpen(overlay, layer) {
    overlay = '#overlay-box-'+overlay;
    //set status to open
    isOpen = true;
    showOverlayBox(overlay, layer);
    if (layer) {
        $('.background-cover-top').css({opacity: 0}).animate({opacity: 0.5, backgroundColor: '#000'});
    } else {
        $('.background-cover').css({opacity: 0}).animate({opacity: 0.5, backgroundColor: '#000'});
    }
    // dont follow the link : so return false.
    return false;
}

function doOverlayClose(overlay, layer) {
    overlay = '#overlay-box-'+overlay;
    //set status to closed
    isOpen = false;
    $(overlay).css('display', 'none');
    // now animate the background to fade out to opacity 0
    // and then hide it after the animation is complete.
    if (layer) {
        $('.background-cover-top').animate( {opacity: 0}, 'fast', null, function() { $(this).hide(); } );
        $(overlay).css({ 'z-index': $(overlay).css('z-index')-layer });
    } else {
        $('.background-cover').animate( {opacity: 0}, 'fast', null, function() { $(this).hide(); } );
    }
}

function doOverlaySwap(close_overlay, open_overlay) {
    // close the current overlay
    overlay = '#overlay-box-'+close_overlay;
    //set status to closed
    isOpen = false;
    $(overlay).css('display', 'none');
    // open the next overlay
    overlay = '#overlay-box-'+open_overlay;
    //set status to open
    isOpen = true;
    showOverlayBox(overlay);
    return false;
}


/* Main Functions */
function cancelOverlay(e) {
    var keyCode;
    if (e == null) {
        keyCode = event.keyCode;
    } else { // mozilla
        keyCode = e.which;
    }
    if (keyCode == 27) {
        if (formID.match('_form')) {
            $('#'+formID+' .cancel_button').trigger('click');
        } else {
            $('#'+formID+'_form .cancel_button').trigger('click');
        }
        formID  = '';
    }
    cancelForm(formID, formID);
}

function cancelForm(event, id) {
    var thisId  = id ? id : this.id;
    var parts   = thisId.split('_');
    var display = parts[1];
    $('#'+display+'_form').find('input').each(function(){
        if ($(this).attr('type') == 'text') {
            if ($(this).id != 'pushupsHashtags' || $(this).id != 'pushupsMentions') {
                $(this).attr('value', '');
            }
        }
    });
    if (isPhone) {
        $('#entry_form').hide();
        $('#middle').show();
    } else {
        doOverlayClose(display);
    }
}

function submitEntryForm(event, id) {
    var thisId  = id ? id : this.id;
    var parts   = thisId.split('_');
    var display = parts[1];
    var action  = parts[2];
    formID      = display
    if (validateForm(display, id)) {
        return false;
    }
    if (action == 'edit') {
        action += '/'+$('#pushupsID').val();
    }
    var params  = $('#entry_form').serialize();
    $.ajax(
        {
            url: '/REST/forms/'+action,
            type: 'post',
            data: params,
            timeout: 10000,
            error: failedEntryForm,
            success: updateEntryForm,
        }
    );
}

function submitOrder(event, id) {
    var params = $('#order-form').serialize();
    $.ajax(
        {
            url: '/REST/forms/new',
            type: 'post',
            data: params,
            timeout: 10000,
            error: failedEntryForm,
            success: updateOrderList,
        }
    );
}

function submitPayPal(event, id) {
    $('#amount').attr('value', this.innerHTML);
    $('#item_number').attr('value', this.id);
    $('#shopping_url').attr('value', $('#shopping_url').val() + this.id);
    $('#pay-now').submit();
//    $.getJSON('/REST/forms/paid/'+this.id, updatePayPal);
}

function showEntryForm(event) {
    $('#title').html('Create');
    $('.edit-form').hide();
    $('.view-form').hide();
    $('.create-form').show();
    formID      = 'entry'
    if (isPhone) {
        $('#entry_form').show();
        $('#middle').hide();
    } else {
        doOverlayOpen(formID);
    }
}

function showViewEntry(event) {
    //alert("showObjectDetails ");
    var classes = $(this).attr('class').split(' ');
    var parts   = this.id.split('_');
    var action  = parts[0];
    var id      = parts[1];
    formID      = 'entry';
    $.getJSON('/REST/forms/view/'+id, populateForm);
    if (action == 'edit') {
        $('#title').html('Edit');
        $('.view-form').hide();
        $('.create-form').hide();
        $('.edit-form').show();
    } else {
        $('#title').html('View');
        $('.edit-form').hide();
        $('.create-form').hide();
        $('.view-form').show();
    }
    if (isPhone) {
        $('#entry_form').show();
        $('#middle').hide();
    } else {
        doOverlayOpen('entry');
    }
}

function showIndexPage(event) {
    window.location.href = '/';
}

function showReports(event) {
    window.location.href = '/reports';
}

function showImage(event) {
    var src = 'http://fundraiser.thaiandhien.com/fundraiser-bree-2012/'+this.id+'.jpg';
    formID  = 'image';
    $('#image_layer_src').attr('src', src);
    doOverlayOpen(formID, 25);
}

function closeImage(event) {
    formID = 'image';
    doOverlayClose(formID, 25);
}

function reloadPage() {
    window.location.reload();
}

function deleteEntry(event) {
    var thisId = id ? id : this.id;
    var parts  = thisId.split('_');
    var id     = parts[1];
    $.getJSON('/REST/forms/delete/'+id, updateEntryForm);
}

function failedEntryForm(data) {
    if (data['status'] == 500) data['message'] = data['status'] + ': ' + data['statusText'];
    updateStatus(data);
}

function updateEntryForm(data) {
    doOverlayClose('entry');
    updateStatus(data);
    if (data['status'] != 200) return;
    if (isPhone) {
        window.location.replace('/iphone');
    } else {
        window.location.replace('/');
    }
}

function updatePayPal(data) {
    $('#pay-now').submit();
    return;
}

function updateOrderList(data) {
    updateStatus(data);
    if (data['status'] != 200) return;
    window.location.reload();
}

function updateStatus(data) {
//          //alert("updateStatus ");
    if (tID) clearTimeout(tID);
    var status_msg = $('#message');
    if (data['status'] != 200) {
        status_msg.css('color','red');
    } else {
        status_msg.css('color','green');
    }
    status_msg.html(data['message']);
    clearMessage();
}

function populateForm(data) {
    $('#pushupsID').val(data['entry']['id']);
    $('#pushupsCreatedDate').val(data['entry']['createdDate']);
    $('#pushupsSet1').val(data['entry']['set1']);
    $('#pushupsSet2').val(data['entry']['set2']);
    $('#pushupsSet3').val(data['entry']['set3']);
    $('#pushupsSet4').val(data['entry']['set4']);
    $('#pushupsSet5').val(data['entry']['set5']);
    $('#pushupsSet6').val(data['entry']['set6']);
    $('#pushupsSet7').val(data['entry']['set7']);
    $('#pushupsExhaust').val(data['entry']['exhaust']);
    $('#pushupsHashtags').val(data['entry']['hashtag']);
    $('#pushupsMentions').val(data['entry']['mentions']);
    $('#pushupsWeek').val(data['entry']['week']);
    $('#pushupsDay').val(data['entry']['day']);
    $('#pushupsLevel').val(data['entry']['level']);
}

function validateForm(object, id) {
    var required = new Array('Exhaust');
    var title    = 'Entry Info ';
    var error    = false;
    for (key in required) {
        var field = required[key].replace(/ /g, '');
        var value = $('#pushups'+field).val();
        if (!value) {
            $('#pushups'+field+'Label').css('color', '#FF0000');
            message = {
                'status': 404,
                'message': title +required[key]+' is Required'
            };
            updateStatus(message);
            error = true;
        } else {
            $('#pushups'+field+'Label').css('color', '#000000');
        }
    }
    return error;
}

function approveRelease(event) {
    doOverlayOpen('loading');
    $.getJSON('/REST/release/approve/'+$('#releaseId').val(), updateApproveStatus);
}

function approveReleaseList(event, id) {
    var itemId = id ? id : this.id;
    var parts  = itemId.split('_');
    var releaseId = parts[1];
    doOverlayOpen('loading');
    $.getJSON('/REST/release/approve/'+releaseId, updateApproveStatusList);
}

function getProjects(event, id) {
    var itemId = id ? id : this.id;
    var selected = $('#'+itemId+' option:selected');
    doOverlayOpen('loading');
    $.getJSON('/REST/release/projects', updateProjectList);
}

function getEnvironments(event, id) {
    var selected = $('#releaseProject option:selected');
    doOverlayOpen('loading');
    $.getJSON('/REST/release/environments/'+selected.val(), updateEnvironmentList);
}

function getBuilds(event, id) {
    var itemId = id ? id : this.id;
    var selected = $('#'+itemId+' option:selected');
    doOverlayOpen('loading');
    $.getJSON('/REST/release/builds/'+selected.val(), updateBuildList);
}
