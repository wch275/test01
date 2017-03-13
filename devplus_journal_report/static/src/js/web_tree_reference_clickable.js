//-*- coding: utf-8 -*-


openerp.devplus_journal_report = function(instance, local)
{
    instance.web.list.Column.include({
        /*
        Load config parameter at init and store it in an accessible variable.
        */
        init: function(id, tag, attrs) {
            this._super(id, tag, attrs);
            if (this.widget == 'reference_clickable') {
                this.use_reference_clickable = true;
            } 
        },

        _format: function (row_data, options)
        {
        	if (this.use_reference_clickable && (row_data['ref__display'] != undefined) ) {
            	var ref_relation=row_data[this.id].value;
            	var ref_val = ref_relation.split(",");
                return _.str.sprintf('<a class="oe_form_uri" data-reference-clickable-model="%s" data-reference-clickable-id="%s">%s</a>',
                		ref_val[0],
                		ref_val[1],
                		row_data['ref__display'].value);
            }
            else {
                return this._super(row_data, options);
            }
        },

	});

    /* reference_clickable widget */

    instance.web.list.columns.add(
            'field.reference_clickable',
            'instance.devplus_journal_report.ReferenceClickable');

    instance.devplus_journal_report.ReferenceClickable = openerp.web.list.Column.extend({
    });

    /* click action */

    instance.web.ListView.List.include({
        render: function()
        {
            var result = this._super(this, arguments),
                self = this;
            this.$current.delegate('a[data-reference-clickable-model]',
                'click', function()
                {
                    self.view.do_action({
                        type: 'ir.actions.act_window',
                        res_model: jQuery(this).data('reference-clickable-model'),
                        res_id: jQuery(this).data('reference-clickable-id'),
                        views: [[false, 'form']],
                    });
                });
            return result;
        },
    });
}
