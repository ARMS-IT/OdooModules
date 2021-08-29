odoo.define('portal_employee.custom', function(require) {
    "use strict";
    require('web.dom_ready');
    var ajax = require('web.ajax');
    var sAnimations = require('website.content.snippets.animation');
    var publicWidget = require('web.public.widget');

    sAnimations.registry.employeeDetails = publicWidget.Widget.extend({
        selector: '.o_portal_wrap',
        events: {
            'change .o_forum_file_upload': '_onChangeFileUpload',
            'change input[name="from_date"]': '_onFromDateChange',
            'change input[name="to_date"]': '_onToDateChange',
            'click .edit_profile': '_editProfile',
            'click .save_profile': '_saveProfile',
            'click .o_forum_profile_pic_clear': '_clearPicture',
            'click .o_forum_profile_pic_edit': '_editPicture',
            'click #new_leave_request': '_newLeaveRequest',
            'click #request': '_request',
        },
        init: function() {
            this._super.apply(this, arguments);
        },
        start: function() {
            var def = this._super.apply(this, arguments);
            return def;
        },
        _onChangeFileUpload: function(ev) {
            if (!ev.currentTarget.files.length) {
                return;
            }
            var $form = $(ev.currentTarget).closest('form');
            var reader = new window.FileReader();
            reader.readAsDataURL(ev.currentTarget.files[0]);
            reader.onload = function(ev) {
                $form.find('.o_forum_avatar_img').attr('src', ev.target.result);
                $('input[name="image_base64"]').val(ev.target.result);
            };
            $form.find('#forum_clear_image').remove();
        },
        _editPicture: function(ev) {
            ev.preventDefault();
            this.$('.o_forum_file_upload').trigger('click');
        },
        _clearPicture: function(ev) {
            var $form = $(this).closest('form');
            this.$('.o_forum_avatar_img').attr("src", "/web/static/src/img/placeholder.png");
            $form.append($('<input/>', {
                name: 'clear_image',
                id: 'forum_clear_image',
                type: 'hidden',
            }));
        },
        _editProfile: function() {
            $('.employee_profile').css('display', 'none');
            $('.employee_profile_form').css('display', 'block');
        },
        _saveProfile: function(ev) {
            var name = this.$('input[name="name"]').val();
            var image = this.$('input[name="image_base64"]').val();
            var private_street = this.$('input[name="private_street"]').val()
            var private_street2 = this.$('input[name="private_street2"]').val()
            var private_state_id = this.$('select[name="private_state_id"]').val()
            var private_zip = this.$('input[name="private_zip"]').val()
            var private_country_id = this.$('select[name="private_country_id"]').val()
            var identification_id = this.$('input[name="identification_id"]').val()
            var passport_id = this.$('input[name="passport_id"]').val()
            var acc_number = this.$('input[name="acc_number"]').val()
            var bank_name = this.$('input[name="bank_name"]').val()
            var gender = this.$('select[name="gender"]').val()
            var marital_status = this.$('select[name="marital_status"]').val()
            var birthday = this.$('input[name="birthday"]').val()
            ajax.jsonRpc('/employee/profile/update_json', 'call', {
                'name': name,
                'image': image,
                'private_street': private_street,
                'private_street2': private_street2,
                'private_state_id': private_state_id,
                'private_zip': private_zip,
                'private_country_id': private_country_id,
                'identification_id': identification_id,
                'passport_id': passport_id,
                'acc_number': acc_number,
                'bank_name': bank_name,
                'gender': gender,
                'marital_status': marital_status,
                'birthday': birthday,
            }).then(function(data) {
                $('.employee_profile_form').first().before(data.render_employee_data);
                $('.employee_profile_form').first().replaceWith(data.render_employee_form);
            });
        },
        _newLeaveRequest: function() {
            $('.leave_data_section').css('display', 'none');
            $('.leave_form_section').css('display', 'block');
        },
        _onFromDateChange: function() {
            var from_date = this.$('input[name="from_date"]').val();
            var to_date = this.$('input[name="to_date"]').val();
            ajax.jsonRpc('/calculate/number_of_days', 'call', {
                'from_date': from_date,
                'to_date': to_date,
            }).then(function(data) {
                $('.duration').text(data);
            });
        },
        _onToDateChange: function() {
            var from_date = this.$('input[name="from_date"]').val();
            var to_date = this.$('input[name="to_date"]').val();
            ajax.jsonRpc('/calculate/number_of_days', 'call', {
                'from_date': from_date,
                'to_date': to_date,
            }).then(function(data) {
                $('.duration').text(data);
            });
        },
        _request: function() {
            var from_date = this.$('input[name="from_date"]').val();
            var to_date = this.$('input[name="to_date"]').val();
            var holiday_status_id = this.$('select[name="leave_type"]').val();
            var description = this.$('textarea[name="description"]').val();
            var number_of_days = this.$('.duration').text();
            ajax.jsonRpc('/leave/update_json', 'call', {
                'from_date': from_date,
                'to_date': to_date,
                'holiday_status_id': holiday_status_id,
                'description': description,
                'number_of_days': number_of_days,
            }).then(function(data) {
                 $('.leave_form_section').first().before(data.leave_data);
                 $('.leave_form_section').first().replaceWith(data.render_leave_form);
            });
        }
    });
});