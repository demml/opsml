from enum import Enum


class HuggingFaceTask(str, Enum):
    AUDIO_CLASSIFICATION = "audio-classification"
    AUTOMATIC_SPEECH_RECOGNITION = "automatic-speech-recognition"
    CONVERSATIONAL = "conversational"
    DEPTH_ESTIMATION = "depth-estimation"
    DOCUMENT_QUESTION_ANSWERING = "document-question-answering"
    FEATURE_EXTRACTION = "feature-extraction"
    FILL_MASK = "fill-mask"
    IMAGE_CLASSIFICATION = "image-classification"
    IMAGE_SEGMENTATION = "image-segmentation"
    IMAGE_TO_IMAGE = "image-to-image"
    IMAGE_TO_TEXT = "image-to-text"
    MASK_GENERATION = "mask-generation"
    OBJECT_DETECTION = "object-detection"
    QUESTION_ANSWERING = "question-answering"
    SUMMARIZATION = "summarization"
    TABLE_QUESTION_ANSWERING = "table-question-answering"
    TEXT2TEXT_GENERATION = "text2text-generation"
    TEXT_CLASSIFICATION = "text-classification"
    TEXT_GENERATION = "text-generation"
    TEXT_TO_AUDIO = "text-to-audio"
    TOKEN_CLASSIFICATION = "token-classification"
    TRANSLATION = "translation"
    TRANSLATION_XX_TO_YY = "translation_xx_to_yy"
    VIDEO_CLASSIFICATION = "video-classification"
    VISUAL_QUESTION_ANSWERING = "visual-question-answering"
    ZERO_SHOT_CLASSIFICATION = "zero-shot-classification"
    ZERO_SHOT_IMAGE_CLASSIFICATION = "zero-shot-image-classification"
    ZERO_SHOT_AUDIO_CLASSIFICATION = "zero-shot-audio-classification"
    ZERO_SHOT_OBJECT_DETECTION = "zero-shot-object-detection"


GENERATION_TYPES = [
    HuggingFaceTask.MASK_GENERATION.value,
    HuggingFaceTask.TEXT_GENERATION.value,
    HuggingFaceTask.TEXT2TEXT_GENERATION.value,
]


class HuggingFaceORTModel(str, Enum):
    ORT_AUDIO_CLASSIFICATION = "ORTModelForAudioClassification"
    ORT_AUDIO_FRAME_CLASSIFICATION = "ORTModelForAudioFrameClassification"
    ORT_AUDIO_XVECTOR = "ORTModelForAudioXVector"
    ORT_CUSTOM_TASKS = "ORTModelForCustomTasks"
    ORT_CTC = "ORTModelForCTC"
    ORT_FEATURE_EXTRACTION = "ORTModelForFeatureExtraction"
    ORT_IMAGE_CLASSIFICATION = "ORTModelForImageClassification"
    ORT_MASKED_LM = "ORTModelForMaskedLM"
    ORT_MULTIPLE_CHOICE = "ORTModelForMultipleChoice"
    ORT_QUESTION_ANSWERING = "ORTModelForQuestionAnswering"
    ORT_SEMANTIC_SEGMENTATION = "ORTModelForSemanticSegmentation"
    ORT_SEQUENCE_CLASSIFICATION = "ORTModelForSequenceClassification"
    ORT_TOKEN_CLASSIFICATION = "ORTModelForTokenClassification"
    ORT_SEQ2SEQ_LM = "ORTModelForSeq2SeqLM"
    ORT_SPEECH_SEQ2SEQ = "ORTModelForSpeechSeq2Seq"
    ORT_VISION2SEQ = "ORTModelForVision2Seq"
    ORT_PIX2STRUCT = "ORTModelForPix2Struct"
    ORT_CAUSAL_LM = "ORTModelForCausalLM"
    ORT_OPTIMIZER = "ORTOptimizer"
    ORT_QUANTIZER = "ORTQuantizer"
    ORT_TRAINER = "ORTTrainer"
    ORT_SEQ2SEQ_TRAINER = "ORTSeq2SeqTrainer"
    ORT_TRAINING_ARGUMENTS = "ORTTrainingArguments"
    ORT_SEQ2SEQ_TRAINING_ARGUMENTS = "ORTSeq2SeqTrainingArguments"
    ORT_STABLE_DIFFUSION_PIPELINE = "ORTStableDiffusionPipeline"
    ORT_STABLE_DIFFUSION_IMG2IMG_PIPELINE = "ORTStableDiffusionImg2ImgPipeline"
    ORT_STABLE_DIFFUSION_INPAINT_PIPELINE = "ORTStableDiffusionInpaintPipeline"
    ORT_STABLE_DIFFUSION_XL_PIPELINE = "ORTStableDiffusionXLPipeline"
    ORT_STABLE_DIFFUSION_XL_IMG2IMG_PIPELINE = "ORTStableDiffusionXLImg2ImgPipeline"
