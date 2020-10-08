import numpy as np
from torch import unsqueeze
from torchvision import transforms
from facenet_pytorch import MTCNN, InceptionResnetV1, fixed_image_standardization


class Extractor:

    def __init__(self):
        self.detector = MTCNN(keep_all=True, min_face_size=40)
        self.encoder = InceptionResnetV1(
            classify=False,
            pretrained='vggface2'
        ).to('cpu')
        _ = self.encoder.eval()
        self.threshold = 0.90
        self.pil2tensor = transforms.Compose([np.float32, transforms.ToTensor(), fixed_image_standardization])

    def extract_faces_embeddings(self, img) -> np.ndarray:
        """Extracts face encodings from a single image"""
        boxes, probs = self.detector.detect(img=img, landmarks=False)
        if boxes is not None:
            for i, (box, prob) in enumerate(zip(boxes, probs)):
                if prob > self.threshold:
                    w = self.detector.image_size
                    face = img.crop(box=box).resize(size=(w, w), resample=2)
                    face = unsqueeze(self.pil2tensor(face), dim=0)
                    yield self.encoder(face).detach().numpy()[0], box, prob
