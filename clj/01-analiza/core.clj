(ns analiza.core
  (:require [clojure.string :as str]))

(defn sum-by-name [file name]
  (let [f (slurp file)
        lines (str/split-lines f)
        filtered-lines (filter #(str/includes? % (subs name 1 (- (count name) 1))) lines)
        values (map #(Float/parseFloat (nth (str/split % #",") 1)) filtered-lines)]
    (apply + values)))

(do
  (print "Enter file: ")
  (flush)
  (let [fajl (read-line)]
    (print "Enter name: ")
    (flush)
    (let [ime (read-line)]
      (println "File: " fajl " name: " ime)
        (println "Sum by name " ime ": " (format "%.3f" (sum-by-name fajl ime))))))