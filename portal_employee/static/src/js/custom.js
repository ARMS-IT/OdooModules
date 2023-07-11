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
            'change .manager_o_forum_file_upload': '_onChangeFileUploadManager',
            'change input[name="from_date"]': '_onFromDateChange',
            'change input[name="to_date"]': '_onToDateChange',
            'click .edit_profile': '_editProfile',
            'click .save_profile': '_saveProfile',
            'click .o_forum_profile_pic_clear': '_clearPicture',
            'click .o_forum_profile_pic_edit': '_editPicture',
            'click .manager_o_forum_profile_pic_clear': '_clearPictureManager',
            'click .manager_o_forum_profile_pic_edit': '_editPictureManager',
            'click #new_leave_request': '_newLeaveRequest',
            'click #request': '_request',
            'click img': '_getChild_data',
            'click .update_profile_info': '_updateProfileInfo',
            'click .save_profiles': '_saveProfiles',
            'click #approve_leave': '_ApproveLeave',
            'click #refuse_leave': '_RefuseLeave',
        },
        init: function() {
            this._super.apply(this, arguments);
        },
        start: function() {
            var self = this;
            var def = this._super.apply(this, arguments);
            self.renderEmployeeDetails();
            return def;
        },
        _ApproveLeave: function(event) {
            var leave_id = parseInt($(event.currentTarget).attr('data-leave-id'));
            ajax.jsonRpc('/approve/leave_update_json', 'call', {
                'leave_id': leave_id
            }).then(function(data) {
                $('.leave_data_section').replaceWith(data.leave_data);
            });
        },
        _RefuseLeave: function(event) {
            var leave_id = parseInt($(event.currentTarget).attr('data-leave-id'));
            ajax.jsonRpc('/refuse/leave_update_json', 'call', {
                'leave_id': leave_id
            }).then(function(data) {
                $('.leave_data_section').replaceWith(data.leave_data);
            });
        },
        _updateProfileInfo: function(event) {
            var employee_id = parseInt($(event.currentTarget).attr('t-att-data-employee-id'));
            ajax.jsonRpc('/manager/employee/profile/update_json', 'call', {
                'employee_id': employee_id
            }).then(function(data) {
                $('#o_organizational_chart').replaceWith(data.render_employee_form);
            });
        },
        _saveProfiles: function(event) {
            var self = this;
            var emp_id = this.$('#o_organizational_chart input[name="employee_id"]').val();
            var name = this.$('#o_organizational_chart input[name="name"]').val();
            var image = this.$('#o_organizational_chart input[name="image_base64"]').val();
            var private_street = this.$('#o_organizational_chart input[name="private_street"]').val()
            var private_street2 = this.$('#o_organizational_chart input[name="private_street2"]').val()
            var private_state_id = this.$('#o_organizational_chart select[name="private_state_id"]').val()
            var private_zip = this.$('#o_organizational_chart input[name="private_zip"]').val()
            var private_country_id = this.$('#o_organizational_chart select[name="private_country_id"]').val()
            var identification_id = this.$('#o_organizational_chart input[name="identification_id"]').val()
            var passport_id = this.$('#o_organizational_chart input[name="passport_id"]').val()
            var acc_number = this.$('#o_organizational_chart input[name="acc_number"]').val()
            var bank_name = this.$('#o_organizational_chart input[name="bank_name"]').val()
            var gender = this.$('#o_organizational_chart select[name="gender"]').val()
            var marital_status = this.$('#o_organizational_chart select[name="marital_status"]').val()
            var birthday = this.$('#o_organizational_chart input[name="birthday"]').val()
            ajax.jsonRpc('/save/employee/profile/update_json', 'call', {
                'emp_id': parseInt(emp_id),
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
                $('#o_organizational_chart').replaceWith(data.render_o_organizational_chart);
                self.renderEmployeeDetails();
            });
            self.renderEmployeeDetails();
        },
        renderEmployeeDetails: function() {
            var employee_id = 1
            var self = this;
            this._rpc({
                route: '/get/parent/employee',
            }).then(function(result) {
                self.parent_len = result[1];
                $.ajax({
                    url: '/get/parent/child',
                    type: 'POST',
                    data: JSON.stringify(result[0]),
                    success: function(value) {
                        $('#o_parent_employee').append(value);
                    },
                });

            });

        },
        _getChild_data: function(events) {
            console.log(events)
            if (events.target.parentElement.className) {
                var self = this
                this.id = events.target.parentElement.id;
                this.check_child = $("#" + this.id + ".o_level_1");
                if (this.check_child[0]) {
                    this.colspan_td = this.check_child[0].parentElement.parentElement
                    this.tbody_child = this.colspan_td.parentElement.parentElement
                    var child_length = this.tbody_child.children.length
                    if (child_length == 1) {
                        this._rpc({
                            route: '/get/parent/colspan',
                            params: {
                                emp_id: parseInt(this.id),
                            },
                        }).then(function(col_val) {
                            if (col_val) {
                                self.colspan_td.colSpan = col_val;
                            }
                        });
                        this._rpc({
                            route: '/get/child/data',
                            params: {
                                click_id: parseInt(this.id),
                            },
                        }).then(function(result) {
                            if (result) {
                                $(result).appendTo(self.tbody_child);
                            }
                        });
                    } else {
                        for (var i = 0; i < 3; i++) {
                            this.tbody_child.children[1].remove();
                        }
                        self.colspan_td.colSpan = 2;
                    }

                }
            }
        },
        _onChangeFileUploadManager: function(ev) {
            if (!ev.currentTarget.files.length) {
                return;
            }
            var $form = $(ev.currentTarget).closest('form');
            var reader = new window.FileReader();
            reader.readAsDataURL(ev.currentTarget.files[0]);
            reader.onload = function(ev) {
                $('#o_organizational_chart').find('.manager_o_forum_avatar_img').attr('src', ev.target.result);
                $('#o_organizational_chart input[name="image_base64"]').val(ev.target.result);
            };
            $form.find('#o_organizational_chart #forum_clear_image').remove();
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
        _editPictureManager: function(ev) {
            ev.preventDefault();
            this.$('#o_organizational_chart .manager_o_forum_file_upload').trigger('click');
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
        _clearPictureManager: function(ev) {
            var $form = $(this).closest('form');
            this.$('#o_organizational_chart .manager_o_forum_avatar_img').attr("src", "/web/static/src/img/placeholder.png");
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
            var self = this;
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