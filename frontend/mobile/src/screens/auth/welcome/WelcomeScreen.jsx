import { useEffect } from 'react';
import { View, Image, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import styles from '../../../styles/authStyles.js';

export default function WelcomeScreen({ navigation }) {
  useEffect(() => {
    const timer = setTimeout(() => navigation.replace('Login'), 1500);
    return () => clearTimeout(timer);
  }, [navigation]);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.welcome}>
        <Image source={require('../../../assets/images/fashion-characters.png')} style={styles.welcomeImage} resizeMode="contain" />
        <Text style={styles.brand}>VirtuFit AI</Text>
      </View>
    </SafeAreaView>
  );
}
