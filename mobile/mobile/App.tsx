import { StatusBar } from 'expo-status-bar';
import { AuthProvider, useAuth } from './src/auth/AuthProvider';
import AudioRecordingScreen from './src/screens/AudioRecordingScreen';
import LoginScreen from './src/screens/LoginScreen';
import { ActivityIndicator, View } from 'react-native';

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f9fafb' }}>
        <ActivityIndicator size="large" color="#4F46E5" />
      </View>
    );
  }

  return isAuthenticated ? <AudioRecordingScreen /> : <LoginScreen />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
      <StatusBar style="auto" />
    </AuthProvider>
  );
}
