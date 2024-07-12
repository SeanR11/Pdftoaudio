import vlc
import GUI
import math
import time
from pathlib import Path
from GUI import Layout, Label, Button, ScaleBar

class MediaPlayer:
    """
    A class to represent a media player widget using VLC for audio playback and PyQt5 for the GUI.
    """
    def __init__(self):
        """
        Initialize the media player with default settings and create necessary attributes.
        """
        self.track = None
        self.track_name = None
        self.player = vlc.MediaPlayer()
        self.track_speed = 1
        self.track_speed_list = [0.5, 1, 1.5, 2]
        self.track_current_time = 0
        self.track_total_time = 0
        self.track_timer = GUI.QTimer()
        self.track_timer.timeout.connect(self.update_player)
        self.track_update_rate = 1000  # Corrected the typo from tracK_update_rate to track_update_rate
        self.track_val = 0
        self.track_timm = None
        self.interactive_buttons = {}
        self.button_size = GUI.QSize(50, 40)

    def load_audio(self, file_path=None, file=None, file_name='DEFAULT'):
        """
        Load audio file into the media player.

        :param file_path: Path to the audio file.
        :param file: Direct audio file content.
        :param file_name: Name of the track.
        """
        if file_path:
            audio_path = GUI.Widget.check_path(file_path, 'audio')
        elif file:
            audio_path = file

        self.track_name = file_name
        if audio_path:
            self.track = vlc.Media(audio_path)
            self.track.parse()
            self.player.set_media(self.track)
            self.track_title.setText(self.track_name)
            self.track_total_time = self.track.get_duration() // 1000
            self.track_total_time_label.setText(self.format_time(self.track_total_time))

    def play(self):
        """
        Play the loaded audio track.
        """
        self.track_timer.start(1000)
        self.player.play()

    def pause(self):
        """
        Pause the currently playing audio track.
        """
        self.player.pause()
        if self.track_timer.isActive():
            self.track_timer.stop()

    def stop(self):
        """
        Stop the currently playing audio track and reset the player.
        """
        self.player.stop()
        self.reset_player()

    def skip_forward(self, seconds):
        """
        Skip forward in the track by a specified number of seconds.

        :param seconds: Number of seconds to skip forward.
        """
        current_time = self.player.get_time()
        self.player.set_time(current_time + (seconds * 1000))

    def skip_backwards(self, seconds):
        """
        Skip backwards in the track by a specified number of seconds.

        :param seconds: Number of seconds to skip backwards.
        """
        current_time = self.player.get_time()
        self.player.set_time(max(0, current_time - (seconds * 1000)))

    def seek(self, seconds):
        """
        Seek to a specific time in the track.

        :param seconds: Time to seek to, in seconds.
        """
        if self.player.get_state() != vlc.State.Playing:
            self.play()
            time.sleep(0.01)
            self.player.set_time(seconds * 1000)
            self.pause()
        else:
            self.player.set_time(seconds * 1000)

    def set_speed(self, speed):
        """
        Set the playback speed of the track.

        :param speed: Playback speed (e.g., 0.5, 1, 1.5, 2).
        """
        self.player.set_rate(speed)

    def switch_speed(self):
        """
        Switch to the next playback speed in the track speed list.
        """
        for index, current_speed in enumerate(self.track_speed_list):
            if current_speed == self.track_speed:
                if index + 1 < len(self.track_speed_list):
                    self.track_speed = self.track_speed_list[index + 1]
                else:
                    self.track_speed = 0.5
                self.set_speed(self.track_speed)
                self.speed_button.update_image(f'assets/img/speed_x{self.track_speed}.png')
                return

    def load_ui(self, container_layout, mode='basic'):
        """
        Load the user interface components for the media player.

        :param container_layout: The layout to place the media player components in.
        :param mode: UI mode (default is 'basic').
        """
        self.mp_main_layout = Layout(container_layout, 'mp_main_layout', 'v')
        self.track_layout = Layout(self.mp_main_layout, 'mp_track_layout', 'h')
        self.bar_layout = Layout(self.mp_main_layout, 'mp_bar_layout', 'h')
        self.buttons_layout = Layout(self.mp_main_layout, 'mp_buttons_layout', 'h')

        self.track_title = Label(self.track_layout, '[ NOT LOADED ]', font_size=18)
        self.track_title.setContentsMargins(0, 5, 0, 0)

        self.track_current_time_label = Label(self.bar_layout, '00:00')
        self.track_bar = ScaleBar(self.bar_layout, name='mp_track_bar', size=GUI.QSize(0, 10), color='coral',
                                  action=self.track_bar_clicked)
        self.track_total_time_label = Label(self.bar_layout, '00:00')

        self.track_bar.add_style('none', 'background-color', 'grey')
        self.track_bar.add_style('none', 'border-radius', '5px')
        self.track_bar.add_style('chunk', 'margin', '0px')
        self.track_bar.add_style('chunk','border-radius','5px')

        self.play_button = Button(self.buttons_layout, name='mp_play_button', icon='assets/img/play_button.png', action=self.play,
                                  size=self.button_size)
        self.pause_button = Button(self.buttons_layout, name='mp_pause_button', icon='assets/img/pause_button.png', action=self.pause,
                                   size=self.button_size)
        self.stop_button = Button(self.buttons_layout, name='mp_stop_button', icon='assets/img/stop_button.png', action=self.stop,
                                  size=self.button_size)
        self.speed_button = Button(self.buttons_layout, name='mp_speed_button', icon='assets/img/speed_x1.png', action=self.switch_speed,
                                   size=self.button_size)

    def format_time(self, seconds):
        """
        Format time in seconds to a MM:SS string format.

        :param seconds: Time in seconds.
        :return: Formatted time string.
        """
        mins, secs = divmod(seconds, 60)
        return f"{mins:02}:{secs:02}"

    def reset_player(self):
        """
        Reset the player to its initial state.
        """
        self.track_current_time = 0
        self.track_bar.setValue(0)
        self.track_current_time_label.setText(self.format_time(self.track_current_time))
        self.track_timer.stop()

    def update_player(self):
        """
        Update the player state, track time, and progress bar.
        """
        if self.track_current_time <= self.track_total_time - 1:
            self.track_current_time = self.player.get_time() // 1000
            self.track_bar.setValue(int((self.track_current_time / self.track_total_time) * 100))
            self.track_current_time_label.setText(self.format_time(self.track_current_time))
        else:
            self.stop()

    def track_bar_clicked(self, event):
        """
        Handle the track bar clicked event to seek to a specific time.

        :param event: The click event on the track bar.
        """
        click_position = event.pos().x() / self.track_bar.width()
        new_track_value = int(
            click_position * (self.track_bar.maximum() - self.track_bar.minimum()) + self.track_bar.minimum())
        self.track_current_time = math.ceil((new_track_value / 100) * self.track_total_time)
        self.track_bar.setValue(new_track_value)
        self.track_current_time_label.setText(self.format_time(self.track_current_time))
        self.seek(self.track_current_time)
