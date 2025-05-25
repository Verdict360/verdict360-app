import { StatusBar } from 'expo-status-bar';
import AudioRecordingScreen from './src/screens/AudioRecordingScreen';

export default function App() {
  return (
    <>
      <AudioRecordingScreen />
      <StatusBar style="auto" />
    </>
  );
}
