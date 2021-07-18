$(function () {
    $('#contactForm').on('submit', function(event) {
        $.ajax({
            data: $(this).serialize(),
            type: $(this).attr('method'),
            url: "/contact-form/",
            success: function() {
                $('#submitSuccessMessage').removeClass('d-none');
                $('#submitButton').attr("disabled",true);
            },
            error: function() {
                $('#submitErrorMessage').removeClass('d-none');
            }
        });
        return false;
    });
})