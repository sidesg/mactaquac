from django import forms

class MediaFileSearchForm(forms.Form):
    item_identifier = forms.CharField(label="item identifier", max_length=55, required=False)
    collection = forms.CharField(label="collection", max_length=15, required=False)
    title = forms.CharField(label="item title", max_length=255, required=False)
    filename = forms.CharField(label="filename", required=False)

class MediaFileFilterForm(forms.Form):
    media_wrapper = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Media Wrapper",
        choices=list()
    )
    video_codec = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Video Codec",
        choices=list()
    )
    audio_codec = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Audio Codec",
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

    def __init__(self, 
            wrapper_list=None,
            vcodec_list=None,
            acodec_list=None,
            *args, **kwargs):
        super(MediaFileFilterForm, self).__init__(*args, **kwargs)
        if wrapper_list:
            self.fields['media_wrapper'].choices = [
                (wrapper, wrapper)
                for wrapper in wrapper_list
            ]
        if vcodec_list:
            self.fields['video_codec'].choices = [
                (vcodec, vcodec)
                for vcodec in vcodec_list
            ]
        if acodec_list:
            self.fields['audio_codec'].choices = [
                (acodec, acodec)
                for acodec in acodec_list
            ]
