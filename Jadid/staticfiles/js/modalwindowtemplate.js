$(function () {


    var loadForm = function () {
        var btn = $(this);
        //generate modal-div name
        var modal_div_name = this.id;

        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function (clicked_button) {
                $('.base-spinner').show();

            },
            success: function (data) {
                $('.base-spinner').hide();
                if (data.status === 'error') {
                    // Handle error
                    alert(data.message);
                    if (data.url_redirect) {

                        $('#error-message').html('<p>'+ data.message + '</p>');
                        window.location.href = data.url_redirect;
                    }
                }
                $("#modal-window .modal-content").html("");   //modal content
                $(modal_div_name + " .modal-content").html(data.html_form);
                $(modal_div_name).modal("show");

            },
            error: function(jqXHR, textStatus, errorThrown) {
                $('.base-spinner').hide();
                // Code to handle errors
                console.log('Error:', textStatus, errorThrown);
                
                // Display a custom message
                alert("An error occurred: " + textStatus + " - " + errorThrown);
        
                // Optionally, you can update the UI with an error message
                $('#error-message').html('<p>An error occurred while processing your request.</p>');
        
                // For debugging, you can log the full response:
                console.log(jqXHR.responseText);
            }
        });
    };

    var loadInfoForm = function () {
        var btn = $(this);
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        $.ajax({
            url: btn.attr("data-url"),
            headers: { 'X-CSRFToken': csrftoken },
            type: 'post',
            dataType: 'json',
            data: { 'target': btn.val() },

            beforeSend: function () {
                $("#modal-window .modal-content").html("");   //modal content
                $("#modal-window").modal("show");
            },
            success: function (data) {
                $("#modal-window .modal-content").html(data.html_form);
            }
        });
    };

    var saveForm = function () {

        if(typeof previewClicked == 'undefined') {
            previewClicked = false;
        }
        var form = $(this);

        $("#id_id.form_control :disabled").removeAttr('disabled');

        const onlyInputs = document.querySelectorAll('#modal-window input');

        onlyInputs.forEach(input => {
            console.log(input);
            input.disabled = false;
        });

        var matchedEle = document.querySelectorAll(".modal.fade.show")[0].id; //find the div name of the modal
        var modalwindow = document.getElementById(matchedEle)
        var modalwindowcontent = modalwindow.getElementsByClassName("modal-content")[0];
        var data = new FormData(form.get(0));

        if(previewClicked) {
            var url = $("#json_import_preview").attr('data-process-url');
        }
        else {
            var url = form.attr("action")
        }
        $.ajax({
            url: url,
            type: form.attr("method"),
            data: data,
            processData: false,
            contentType: false,
            dataType: 'json',
            success: function (data) {
                console.log(previewClicked);
                if(previewClicked == false) {
                    if (data.form_is_valid) {
                        $(modalwindow).modal("hide");
                        if (data.redirect) {
                            var current_location = window.location.href;
                            var hostname = window.location.hostname;

                            //location.replace(current_location + data.pk + "/playgrounddetail/");
                            location.replace(data.redirect_address);
                        }
                        else {
                            location.reload();
                        }

                    }
                    else {
                        $(modalwindowcontent).html(data.html_form);
                    }
                }
                else {
                    $("#json_import_preview").html('<pre style="overflow-y: scroll; overflow-x: hidden; height: 300px;">' + JSON.stringify(data, undefined, 2) + '</pre>');
                    previewClicked = false;
                    var show = false;
                    var tbl_html = "<div style='margin: 20px 15px; font-weight: bold; color: red;'>There are differences between imported values and values stored in our database!</div>";
                    tbl_html  += "<table style='border: 1px solid black; width: 100%; margin: 0px 100px;'>";
                    $.each(data['comparison'], function(key, value) {
                        if (value['flag'] != "REF_CORRECT") {
                            show = true;
                            tbl_html += "<tr style='text-align: center; font-weight: bold; font-size: 16px; border-bottom: 1px solid black;'><td style='border-right: 1px solid black;'>" + key + "</td></tr>"
                            console.log("IN_DATABASE");
                            console.log(value['flag'] != "ORPH_UNIDENTIFIED");
                            if(value['flag'] != "ORPH_UNIDENTIFIED") {
                                tbl_html += "<tr style='font-weight: bold; font-size: 14px; border-bottom: 1px solid black;'><td style='text-align: center;border-right: 1px solid black;'>EC name</td><td style='border-right: 1px solid black;'>DB value</td><td style='border-right: 1px solid black;'>Import value</td></tr>"
                                $.each(value['data'], function(k, calculations) {
                                    if (!calculations['same_value']) {
                                        tbl_html += "<tr style='font-size: 14px;'><td style='text-align: center;border-right: 1px solid black;'>" + k + "</td><td style='border-right: 1px solid black;'>" + calculations['db_process'] + "</td><td style='background: #ff7853;border-right: 1px solid black;'>" + calculations['json_Process'] + "</td></tr>"
                                    }
                                });
                            }
                            else {
                                tbl_html += "<tr style='font-weight: bold; font-size: 14px; border-bottom: 1px solid black;'><td style='text-align: center; color: #af1a1a;'>PROCESS NOT PRESENT IN DATABASE</td></tr>"

                            }
                            console.log(key, value);
                        }
                    });
                    tbl_html += "</table>";
                    if(show) {
                        $("#json_import_diff").html(tbl_html);
                    }
                    else {
                        tbl_html = "<div style='margin: 20px 15px; font-weight: bold; color: green;'>Import values correspond with current database.</div>";
                        $("#json_import_diff").html(tbl_html);
                    }
                }

            }
        });
        return false;
    };


    // Create object - Open
    //$(".js-object-create").click(loadForm);
    $(document).on("click", ".js-object-create", loadForm);
    // Create object - Submit
    //$("#modal-form").on("submit", ".js-object-create-form", saveForm);
    $("#modal-window").on("submit", ".js-object-create-form", saveForm);
    $("#modal-window-xl").on("submit", ".js-object-create-form", saveForm);
    $("#modal-window-lg").on("submit", ".js-object-create-form", saveForm);
    // Update object
    $("#objects-container").on("click", ".js-object-update", loadForm);
    $("#modal-window").on("submit", ".js-object-update-form", saveForm);
    $("#modal-window-xl").on("submit", ".js-object-update-form", saveForm);
    $("#modal-window-lg").on("submit", ".js-object-update-form", saveForm);
    // Delete object
    $("#objects-container").on("click", ".js-object-delete", loadForm);
    $("#modal-window").on("submit", ".js-object-delete-form", saveForm);
    $("#modal-window-xl").on("submit", ".js-object-delete-form", saveForm);

    //Info window
    $(".js-modalinfo-create").click(loadInfoForm);



});

