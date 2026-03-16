/**
 * Lab Reports Screen
 * Upload and view soil sample lab reports.
 * Farmer photographs lab report → app parses and stores structured results.
 */
import { Text, View, StyleSheet } from "react-native";

export default function Reports() {
  // TODO: camera/file picker for lab report upload
  // TODO: fetch uploaded reports via useLabReports hook
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Lab Reports</Text>
      {/* TODO: Upload button (camera + file picker) */}
      {/* TODO: Report list with parse status */}
      {/* TODO: Parsed results view */}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#f5f7f5", padding: 16 },
  title: { fontSize: 24, fontWeight: "bold", color: "#1a3a2a" },
});
