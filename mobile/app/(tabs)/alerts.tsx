/**
 * Alerts Screen
 * Critical soil alerts and drought warnings.
 * Goal: farmer understands problem + action in under 10 seconds.
 */
import { Text, View, StyleSheet } from "react-native";

export default function Alerts() {
  // TODO: fetch alerts via useAlerts hook
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Alerts</Text>
      {/* TODO: AlertCard list — critical first, then warnings */}
      {/* TODO: Drought risk banner */}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7f5", padding: 16 },
  title: { fontSize: 24, fontWeight: "bold", color: "#1a3a2a" },
});
