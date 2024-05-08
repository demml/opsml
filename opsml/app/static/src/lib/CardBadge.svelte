<script lang="ts">
    import sklearnLogo from '$lib/images/scikit-learn.svg'
    import tensorflowLogo from '$lib/images/tensorFlow.svg'
    import torchLogo from '$lib/images/PyTorch.svg'
    import catboostLogo from '$lib/images/CatBoostLogo.png'
    import numpyLogo from '$lib/images/NumPy.svg'
    import pandasLogo from '$lib/images/Pandas.svg'


    const logos = {
        'SklearnModel': sklearnLogo,
        'TensorFlowModel': tensorflowLogo,
        'TorchModel': torchLogo,
        'CatBoostModel': catboostLogo,
        'NumpyData': numpyLogo,
        'PandasData': pandasLogo,
        'HuggingFaceModel': "https://cdn-lfs.huggingface.co/repos/96/a2/96a2c8468c1546e660ac2609e49404b8588fcf5a748761fa72c154b2836b4c83/942cad1ccda905ac5a659dfd2d78b344fccfb84a8a3ac3721e08f488205638a0?response-content-disposition=inline%3B+filename*%3DUTF-8%27%27hf-logo.svg%3B+filename%3D%22hf-logo.svg%22%3B&response-content-type=image%2Fsvg%2Bxml&Expires=1712000062&Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTcxMjAwMDA2Mn19LCJSZXNvdXJjZSI6Imh0dHBzOi8vY2RuLWxmcy5odWdnaW5nZmFjZS5jby9yZXBvcy85Ni9hMi85NmEyYzg0NjhjMTU0NmU2NjBhYzI2MDllNDk0MDRiODU4OGZjZjVhNzQ4NzYxZmE3MmMxNTRiMjgzNmI0YzgzLzk0MmNhZDFjY2RhOTA1YWM1YTY1OWRmZDJkNzhiMzQ0ZmNjZmI4NGE4YTNhYzM3MjFlMDhmNDg4MjA1NjM4YTA%7EcmVzcG9uc2UtY29udGVudC1kaXNwb3NpdGlvbj0qJnJlc3BvbnNlLWNvbnRlbnQtdHlwZT0qIn1dfQ__&Signature=xET2ICPq0ZkvA5n7kr4cvZaRFSb6p3%7E1KPx4cADj6TNFKYZ%7ELt96RRICmscKwalXD8IHKp-13KcuK2l%7E5Dxkoo%7EUbnClinXzrcv%7EpMeQxCTWW-AXqT0reUriRKAd-dm8xS%7ECd3fQZuXiicUv0%7E55FB-ed5CGkUqgPYDgkAQHSGvhMtYcG2KhVzBC5U74%7Ec3OMLBUCJrjSR9E54oGm7cRqOdhLKp885mzlSOymCsQo1LO3MJBadBse-9adHwqQMjOsnbfFFu9SbTb4OMMksz9yHOPSNJqmlX7I8aQSKuZxybal7TT54hfBMHJu-rQqxG%7ELl0UXvytU0OXxX8ktRv%7EGg__&Key-Pair-Id=KVTP0A1DKRTAX"
    }

    export let artifactInterface: string = 'SklearnModel'
    

</script>


<div>
    {#if artifactInterface in logos }
        <a class="badge bg-surface-50 border border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
        <img alt="{artifactInterface} logo" class="h-5" src="{logos[artifactInterface]}">
        <span class="text-primary-500">{artifactInterface}</span>
        </a>
    {:else}
        <a class="badge bg-surface-50 border border-surface-300 hover:bg-gradient-to-b from-surface-50 to-surface-100">
        <span class="text-primary-500">{artifactInterface}</span>
        </a>
    {/if}
</div>