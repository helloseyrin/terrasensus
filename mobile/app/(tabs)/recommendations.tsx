/**
 * Recommendations Screen
 * AI-generated fertiliser and supplier recommendations with eco-scores.
 */
import { Text, View, StyleSheet } from "react-native";

export default function Recommendations() {
  // TODO: fetch recommendations via useRecommendations hook
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Recommendations</Text>
      {/* TODO: Crop suitability cards */}
      {/* TODO: Fertiliser recommendations with eco-score badges */}
      {/* TODO: Supplier suggestions with cost estimate */}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7f5", padding: 16 },
  title: { fontSize: 24, fontWeight: "bold", color: "#1a3a2a" },
});
