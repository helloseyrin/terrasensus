/**
 * Field Overview Screen
 * Shows live soil sensor readings for all plots at a glance.
 * Farmer's primary screen — must be readable in sunlight, large touch targets.
 */
import { Text, View, StyleSheet } from "react-native";

export default function FieldOverview() {
  // TODO: fetch live sensor readings via useSensorReadings hook
  return (
    <View style={styles.container}>
      <Text style={styles.title}>TerraSensus</Text>
      <Text style={styles.subtitle}>Field Overview</Text>
      {/* TODO: SensorCard per plot */}
      {/* TODO: Overall soil health score */}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7f5", padding: 16 },
  title: { fontSize: 28, fontWeight: "bold", color: "#1a3a2a" },
  subtitle: { fontSize: 16, color: "#4a7a5a", marginBottom: 24 },
});
