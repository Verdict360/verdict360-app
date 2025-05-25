import React from 'react';
import { ActivityIndicator, Alert, StyleSheet, Text, TouchableOpacity, View } from 'react-native';
import { useAuth } from '../auth/AuthProvider';

export default function LoginScreen() {
  const { login, isLoading } = useAuth();

  const handleLogin = async () => {
    try {
      await login();
    } catch (error) {
      Alert.alert(
        'Authentication Error',
        'Failed to connect to Verdict360. Please check your connection and try again.'
      );
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size='large' color='#4F46E5' />
        <Text style={styles.loadingText}>Connecting to Verdict360...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.logo}>Verdict360</Text>
        <Text style={styles.tagline}>Legal Intelligence Platform</Text>
        <Text style={styles.subtitle}>Mobile Recording Studio</Text>
      </View>

      <View style={styles.content}>
        <View style={styles.featureList}>
          <View style={styles.feature}>
            <Text style={styles.featureIcon}>🎤</Text>
            <Text style={styles.featureText}>Secure Legal Recording</Text>
          </View>
          <View style={styles.feature}>
            <Text style={styles.featureIcon}>🔒</Text>
            <Text style={styles.featureText}>Encrypted Storage</Text>
          </View>
          <View style={styles.feature}>
            <Text style={styles.featureIcon}>📝</Text>
            <Text style={styles.featureText}>Auto Transcription</Text>
          </View>
          <View style={styles.feature}>
            <Text style={styles.featureIcon}>⚖️</Text>
            <Text style={styles.featureText}>South African Legal Compliance</Text>
          </View>
        </View>

        <TouchableOpacity style={styles.loginButton} onPress={handleLogin}>
          <Text style={styles.loginButtonText}>Sign In to Verdict360</Text>
        </TouchableOpacity>

        <Text style={styles.disclaimer}>
          By signing in, you agree to maintain confidentiality of all legal recordings and comply with professional
          standards.
        </Text>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>Secure • Professional • Compliant</Text>
        <Text style={styles.version}>Version 1.0.0</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
    paddingHorizontal: 24,
    paddingTop: 60,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f9fafb',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
  },
  header: {
    alignItems: 'center',
    marginBottom: 48,
  },
  logo: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#4F46E5',
    marginBottom: 8,
  },
  tagline: {
    fontSize: 16,
    color: '#1E293B',
    fontWeight: '500',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
  },
  content: {
    flex: 1,
    justifyContent: 'center',
  },
  featureList: {
    marginBottom: 48,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
    paddingHorizontal: 16,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: 16,
    width: 32,
    textAlign: 'center',
  },
  featureText: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '500',
  },
  loginButton: {
    backgroundColor: '#4F46E5',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  loginButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
  },
  disclaimer: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 18,
    paddingHorizontal: 16,
  },
  footer: {
    alignItems: 'center',
    paddingBottom: 32,
  },
  footerText: {
    fontSize: 12,
    color: '#9CA3AF',
    marginBottom: 4,
  },
  version: {
    fontSize: 10,
    color: '#D1D5DB',
  },
});
