from __future__ import annotations

import typing as T
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class SpectrogramParams:
    """
    Parameters for the conversion from audio to spectrograms to images and back.

    Includes helpers to convert to and from EXIF tags, allowing these parameters to be stored
    within spectrogram images.
    """

    # Whether the audio is stereo or mono
    stereo: bool = False

    # Whether the spectrogram uses R,G,B channels
    # to encode triple resolution of frequency data in mono
    triple_res_mono: bool = False

    # FFT parameters
    sample_rate: int = 44100
    step_size_ms: int = 10
    window_duration_ms: int = 100
    padded_duration_ms: int = 400

    # Mel scale parameters
    num_frequencies: int = 512
    # TODO(hayk): Set these to [20, 20000] for newer models
    min_frequency: int = 0
    max_frequency: int = 10000
    mel_scale_norm: T.Optional[str] = None
    mel_scale_type: str = "htk"
    max_mel_iters: int = 200

    # Griffin Lim parameters
    num_griffin_lim_iters: int = 32

    # Image parameterization
    power_for_image: float = 0.25

    class ExifTags(Enum):
        """
        Custom EXIF tags for the spectrogram image.
        """

        SAMPLE_RATE = 11000
        STEREO = 11005
        TRIPLE_RES_MONO = 11007
        STEP_SIZE_MS = 11010
        WINDOW_DURATION_MS = 11020
        PADDED_DURATION_MS = 11030

        NUM_FREQUENCIES = 11040
        MIN_FREQUENCY = 11050
        MAX_FREQUENCY = 11060

        POWER_FOR_IMAGE = 11070
        MAX_VALUE = 11080

    @property
    def n_fft(self) -> int:
        """
        The number of samples in each STFT window, with padding.
        """
        return int(self.padded_duration_ms / 1000.0 * self.sample_rate)

    @property
    def win_length(self) -> int:
        """
        The number of samples in each STFT window.
        """
        return int(self.window_duration_ms / 1000.0 * self.sample_rate)

    @property
    def hop_length(self) -> int:
        """
        The number of samples between each STFT window.
        """
        return int(self.step_size_ms / 1000.0 * self.sample_rate)

    def to_exif(self) -> T.Dict[int, T.Any]:
        """
        Return a dictionary of EXIF tags for the current values.
        """
        return {
            self.ExifTags.SAMPLE_RATE.value: self.sample_rate,
            self.ExifTags.STEREO.value: self.stereo,
            self.ExifTags.TRIPLE_RES_MONO.value: self.triple_res_mono,
            self.ExifTags.STEP_SIZE_MS.value: self.step_size_ms,
            self.ExifTags.WINDOW_DURATION_MS.value: self.window_duration_ms,
            self.ExifTags.PADDED_DURATION_MS.value: self.padded_duration_ms,
            self.ExifTags.NUM_FREQUENCIES.value: self.num_frequencies,
            self.ExifTags.MIN_FREQUENCY.value: self.min_frequency,
            self.ExifTags.MAX_FREQUENCY.value: self.max_frequency,
            self.ExifTags.POWER_FOR_IMAGE.value: float(self.power_for_image),
        }

    @classmethod
    def from_exif(cls, exif: T.Mapping[int, T.Any]) -> SpectrogramParams:
        """
        Create a SpectrogramParams object from the EXIF tags of the given image.
        """
        return cls(
            sample_rate=exif.get(cls.ExifTags.SAMPLE_RATE.value) or 0,
            stereo=bool(exif.get(cls.ExifTags.STEREO.value)),
            triple_res_mono=bool(exif.get(cls.ExifTags.TRIPLE_RES_MONO.value)),
            step_size_ms=exif.get(cls.ExifTags.STEP_SIZE_MS.value) or 0,
            window_duration_ms=exif.get(cls.ExifTags.WINDOW_DURATION_MS.value) or 0,
            padded_duration_ms=exif.get(cls.ExifTags.PADDED_DURATION_MS.value) or 0,
            num_frequencies=exif.get(cls.ExifTags.NUM_FREQUENCIES.value) or 0,
            min_frequency=exif.get(cls.ExifTags.MIN_FREQUENCY.value) or 0,
            max_frequency=exif.get(cls.ExifTags.MAX_FREQUENCY.value) or 0,
            power_for_image=exif.get(cls.ExifTags.POWER_FOR_IMAGE.value) or 0,
        )
