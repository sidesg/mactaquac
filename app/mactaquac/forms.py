from django import forms

class MediaFileSearchForm(forms.Form):
    item_identifier = forms.CharField(label="item identifier", max_length=55, required=False)
    collection = forms.CharField(label="collection", max_length=15, required=False)
    title = forms.CharField(label="item title", max_length=255, required=False)
    filename = forms.CharField(label="filename", required=False)

    # media_wrapper = forms.CharField(
    #     required=False,
    #     label="Media Wrapper",
    #     max_length=55,
    #     widget=forms.HiddenInput()
    # )
    # dimensions_width = forms.IntegerField(
    #     required=False,
    #     label="Min. width",
    #     widget=forms.HiddenInput()
    # )

class MediaFileFilterForm(forms.Form):
    media_wrapper = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Media Wrapper",
        choices=list()
    )
    dimensions_width = forms.IntegerField(
        required=False,
        label="Min. width"
    )

    item_identifier = forms.CharField(label="item identifier", max_length=55, required=False, widget=forms.HiddenInput())
    collection = forms.CharField(label="collection", max_length=15, required=False, widget=forms.HiddenInput())
    title = forms.CharField(label="item title", max_length=255, required=False, widget=forms.HiddenInput())
    filename = forms.CharField(label="filename", required=False, widget=forms.HiddenInput())

    def __init__(self, wrapper_list=None, *args, **kwargs):
        super(MediaFileFilterForm, self).__init__(*args, **kwargs)
        if wrapper_list:
            self.fields['media_wrapper'].choices = [
                (wrapper, wrapper)
                for wrapper in wrapper_list
            ]
