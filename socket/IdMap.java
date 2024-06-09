import java.util.*;
import java.util.function.BiConsumer;
import java.util.function.BiFunction;
import java.util.function.Function;

public class IdMap<T> {
    private final HashMap<T, Integer> map;
    private int index;
    public IdMap(){
        map = new HashMap<>();
        index = 0;
    }

    public void add(T s) {
        if(!map.containsKey(s)){
            map.put(s, ++index);
        }
    }

    public Integer get(T s) {
        return map.get(s);
    }

    public int size() {
        return map.size();
    }

    /**
     * Returns {@code true} if this map contains no key-value mappings.
     *
     * @return {@code true} if this map contains no key-value mappings
     */
    public boolean isEmpty() {
        return map.isEmpty();
    }



    /**
     * Returns {@code true} if this map contains a mapping for the
     * specified key.
     *
     * @param key The key whose presence in this map is to be tested
     * @return {@code true} if this map contains a mapping for the specified
     * key.
     */
    public boolean containsKey(T key) {
        return map.containsKey(key);
    }

    /**
     * Associates the specified value with the specified key in this map.
     * If the map previously contained a mapping for the key, the old
     * value is replaced.
     *
     * @param key   key with which the specified value is to be associated
     * @param value value to be associated with the specified key
     * @return the previous value associated with {@code key}, or
     * {@code null} if there was no mapping for {@code key}.
     * (A {@code null} return can also indicate that the map
     * previously associated {@code null} with {@code key}.)
     */
    public Integer put(T key, Integer value) {
        return map.put(key, value);
    }

    /**
     * Copies all of the mappings from the specified map to this map.
     * These mappings will replace any mappings that this map had for
     * any of the keys currently in the specified map.
     *
     * @param m mappings to be stored in this map
     * @throws NullPointerException if the specified map is null
     */
    public void putAll(Map<? extends T, ? extends Integer> m) {
        map.putAll(m);
    }

    /**
     * Removes the mapping for the specified key from this map if present.
     *
     * @param key key whose mapping is to be removed from the map
     * @return the previous value associated with {@code key}, or
     * {@code null} if there was no mapping for {@code key}.
     * (A {@code null} return can also indicate that the map
     * previously associated {@code null} with {@code key}.)
     */
    public Integer remove(T key) {
        return map.remove(key);
    }

    /**
     * Removes all of the mappings from this map.
     * The map will be empty after this call returns.
     */
    public void clear() {
        map.clear();
    }

    /**
     * Returns {@code true} if this map maps one or more keys to the
     * specified value.
     *
     * @param value value whose presence in this map is to be tested
     * @return {@code true} if this map maps one or more keys to the
     * specified value
     */
    public boolean containsValue(Integer value) {
        return map.containsValue(value);
    }

    /**
     * Returns a {@link Set} view of the keys contained in this map.
     * The set is backed by the map, so changes to the map are
     * reflected in the set, and vice-versa.  If the map is modified
     * while an iteration over the set is in progress (except through
     * the iterator's own {@code remove} operation), the results of
     * the iteration are undefined.  The set supports element removal,
     * which removes the corresponding mapping from the map, via the
     * {@code Iterator.remove}, {@code Set.remove},
     * {@code removeAll}, {@code retainAll}, and {@code clear}
     * operations.  It does not support the {@code add} or {@code addAll}
     * operations.
     *
     * @return a set view of the keys contained in this map
     */
    public Set<T> keySet() {
        return map.keySet();
    }

    /**
     * Returns a {@link Collection} view of the values contained in this map.
     * The collection is backed by the map, so changes to the map are
     * reflected in the collection, and vice-versa.  If the map is
     * modified while an iteration over the collection is in progress
     * (except through the iterator's own {@code remove} operation),
     * the results of the iteration are undefined.  The collection
     * supports element removal, which removes the corresponding
     * mapping from the map, via the {@code Iterator.remove},
     * {@code Collection.remove}, {@code removeAll},
     * {@code retainAll} and {@code clear} operations.  It does not
     * support the {@code add} or {@code addAll} operations.
     *
     * @return a view of the values contained in this map
     */
    public Collection<Integer> values() {
        return map.values();
    }

    /**
     * Returns a {@link Set} view of the mappings contained in this map.
     * The set is backed by the map, so changes to the map are
     * reflected in the set, and vice-versa.  If the map is modified
     * while an iteration over the set is in progress (except through
     * the iterator's own {@code remove} operation, or through the
     * {@code setValue} operation on a map entry returned by the
     * iterator) the results of the iteration are undefined.  The set
     * supports element removal, which removes the corresponding
     * mapping from the map, via the {@code Iterator.remove},
     * {@code Set.remove}, {@code removeAll}, {@code retainAll} and
     * {@code clear} operations.  It does not support the
     * {@code add} or {@code addAll} operations.
     *
     * @return a set view of the mappings contained in this map
     */
    public Set<Map.Entry<T, Integer>> entrySet() {
        return map.entrySet();
    }

    public Integer getOrDefault(T key, Integer defaultValue) {
        return map.getOrDefault(key, defaultValue);
    }

    public Integer putIfAbsent(T key, Integer value) {
        return map.putIfAbsent(key, value);
    }

    public boolean remove(T key, T value) {
        return map.remove(key, value);
    }

    public boolean replace(T key, Integer oldValue, Integer newValue) {
        return map.replace(key, oldValue, newValue);
    }

    public Integer replace(T key, Integer value) {
        return map.replace(key, value);
    }

    /**
     * {@inheritDoc}
     *
     * <p>This method will, on a best-effort basis, throw a
     * {@link ConcurrentModificationException} if it is detected that the
     * mapping function modifies this map during computation.
     *
     * @param key
     * @param mappingFunction
     * @throws ConcurrentModificationException if it is detected that the
     *                                         mapping function modified this map
     */
    public Integer computeIfAbsent(T key, Function<? super T, ? extends Integer> mappingFunction) {
        return map.computeIfAbsent(key, mappingFunction);
    }

    /**
     * {@inheritDoc}
     *
     * <p>This method will, on a best-effort basis, throw a
     * {@link ConcurrentModificationException} if it is detected that the
     * remapping function modifies this map during computation.
     *
     * @param key
     * @param remappingFunction
     * @throws ConcurrentModificationException if it is detected that the
     *                                         remapping function modified this map
     */
    public Integer computeIfPresent(T key, BiFunction<? super T, ? super Integer, ? extends Integer> remappingFunction) {
        return map.computeIfPresent(key, remappingFunction);
    }

    /**
     * {@inheritDoc}
     *
     * <p>This method will, on a best-effort basis, throw a
     * {@link ConcurrentModificationException} if it is detected that the
     * remapping function modifies this map during computation.
     *
     * @param key
     * @param remappingFunction
     * @throws ConcurrentModificationException if it is detected that the
     *                                         remapping function modified this map
     */
    public Integer compute(T key, BiFunction<? super T, ? super Integer, ? extends Integer> remappingFunction) {
        return map.compute(key, remappingFunction);
    }

    /**
     * {@inheritDoc}
     *
     * <p>This method will, on a best-effort basis, throw a
     * {@link ConcurrentModificationException} if it is detected that the
     * remapping function modifies this map during computation.
     *
     * @param key
     * @param value
     * @param remappingFunction
     * @throws ConcurrentModificationException if it is detected that the
     *                                         remapping function modified this map
     */
    public Integer merge(T key, Integer value, BiFunction<? super Integer, ? super Integer, ? extends Integer> remappingFunction) {
        return map.merge(key, value, remappingFunction);
    }

    public void forEach(BiConsumer<? super T, ? super Integer> action) {

        map.forEach(action);
    }

    public void replaceAll(BiFunction<? super T, ? super Integer, ? extends Integer> function) {
        map.replaceAll(function);
    }
}
