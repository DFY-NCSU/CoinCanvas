extension IterableExtensions<T> on Iterable<T> {
  Iterable<T> sortedBy(Comparable Function(T) keyExtractor) {
    return toList()..sort((a, b) => keyExtractor(a).compareTo(keyExtractor(b)));
  }
}