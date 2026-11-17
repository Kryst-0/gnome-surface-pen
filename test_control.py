import unittest
from unittest.mock import patch
import control

class Actions(unittest.TestCase):
    def test_presentation_detection(self):
        for cls,title in [('libreoffice-impress','Talk'),('okular','Talk.pdf'),('org.gnome.Papers','Talk.pdf'),('org.gnome.Evince','Talk.pdf'),('firefox','Talk - Google Slides')]:
            self.assertTrue(control.presentation({'class':cls,'title':title,'fullscreen':2},'auto'))
            self.assertFalse(control.presentation({'class':cls,'title':title,'fullscreen':0},'auto'))
        self.assertFalse(control.presentation({'class':'foot','fullscreen':2},'auto'))
        self.assertTrue(control.presentation({},'on'))
        self.assertFalse(control.presentation({'class':'libreoffice-impress','fullscreen':2},'off'))
    def test_firefox_pdf_presentation(self):
        title = 'Testo del paragrafo - Testo del paragrafo.pdf — Mozilla Firefox'
        for fullscreen in ({'fullscreen':2}, {'fullscreen':0,'fullscreenClient':2}):
            window = {'class':'firefox','title':title} | fullscreen
            self.assertTrue(control.presentation(window,'auto'))
            self.assertFalse(control.presentation(window,'off'))
        self.assertFalse(control.presentation({'class':'firefox','title':title,'fullscreen':0},'auto'))
        self.assertFalse(control.presentation({'class':'firefox','title':'News — Mozilla Firefox','fullscreen':2},'auto'))
        self.assertFalse(control.presentation({'class':'firefox','title':'test.pdf.exe — Mozilla Firefox','fullscreen':2},'auto'))

    def test_slides_clear_modifiers_and_target_window(self):
        for action,key in [('single','Right'),('double','Left')]:
            with patch('sys.argv',['control.py',action]), patch.object(control,'load',return_value=control.DEFAULT), patch.object(control,'run',side_effect=['{"class":"libreoffice-impress","fullscreen":2,"address":"0x123"}','ok']) as run:
                self.assertEqual(control.main()['action'],'slide')
                self.assertEqual(run.call_args.args[0],['hyprctl','eval', 'hl.dispatch(hl.dsp.send_shortcut({' + f'mods = "", key = "{key}", window = "address:0x123"' + '}))'])
    def test_hyprctl_error_with_success_exit_code(self):
        import subprocess
        with patch.object(control.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'error: Lua failure', '')):
            with self.assertRaises(ValueError):
                control.run(['hyprctl','eval','invalid'])

    def test_apps_launch_without_shell(self):
        with patch('sys.argv',['control.py','single']), patch.object(control,'load',return_value=control.DEFAULT|{'single':'test.desktop'}), patch.object(control,'run',return_value='{}'), patch.object(control,'apps',return_value=[{'id':'test.desktop','path':'/tmp/a $().desktop'}]), patch.object(control.subprocess,'Popen') as popen:
            control.main()
            self.assertEqual(popen.call_args.args[0],['gio','launch','/tmp/a $().desktop'])

if __name__=='__main__':unittest.main()
