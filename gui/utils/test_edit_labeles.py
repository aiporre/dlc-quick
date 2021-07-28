from unittest import TestCase

from gui.utils.edit_labeles import Labels, edit_labels


class TestLabels(TestCase):

    @classmethod
    def setUp(self) -> None:
        self.config = "/Users/ariel/funana/projects-whisker/wtfree5ma-agkuner-2021-06-25/config.yaml"
        self.video = "#46_2020-10-25_P3.9_ruleswitch_two_textures_punishrepeat_session59_videos_hispeed1_video_sec10"
        self.labels = Labels(self.config, self.video)

    def test_get_individuals(self):
        print(self.labels.get_individuals())

    def test_remove_individual(self):
        print(self.labels.remove_individual('wR4'))


class TestMainEditLabels(TestCase):
    def test_main_remove(self):
        config = "/Users/ariel/funana/projects-whisker/wtfree5ma-agkuner-2021-06-25/config.yaml"
        video = "#46_2020-10-25_P3.9_ruleswitch_two_textures_punishrepeat_session59_videos_hispeed1_video_sec10"
        edit_labels(config, video, remove=True, individuals=['wR4', 'wL4'])
    def test_main_rollback(self):
        config = "/Users/ariel/funana/projects-whisker/wtfree5ma-agkuner-2021-06-25/config.yaml"
        video = "#46_2020-10-25_P3.9_ruleswitch_two_textures_punishrepeat_session59_videos_hispeed1_video_sec10"
        edit_labels(config, video, remove=False, rollback=True)
