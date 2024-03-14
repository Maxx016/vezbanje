(ns labapp.core
  (:require [clojure.tools.cli :refer [parse-opts]]
            [clojure.string :as str]
            [next.jdbc :as jdbc]
            [next.jdbc.date-time]
            [next.jdbc.sql :as sql]
            [tech.v3.dataset :as ds]
            [tech.v3.dataset.print :as ds.print])
  (:import [java.time.format DateTimeParseException]
           [java.time.format DateTimeFormatter])
  (:gen-class))

(def db (jdbc/get-datasource {:dbtype "sqlite" :dbname "database.db"}))

(defn valid-datetime? [s]
  (try
    (let [formatter (DateTimeFormatter/ofPattern "yyyy-MM-dd HH:mm:ss")]
      (.parse formatter s)
      true)
    (catch DateTimeParseException e
      false)))

(defn valid-uuid? [s]
  (try
    (java.util.UUID/fromString s)
    true
    (catch IllegalArgumentException _ false)))

(defn timestamp []
  (let [timestamp (java.time.LocalDateTime/now)
        formatter (DateTimeFormatter/ofPattern "yyyy-MM-dd HH:mm:ss")]
    (.format formatter timestamp)))

(def cli-opts
  [["-id" "--id UUID4" "UUID4 merenja (pregled/brisanje/promena)"
    :validate [#(valid-uuid? %) "Mora biti validna UUID vrednost"]]
   ["-n" "--naziv NAZIV" "Naziv merenja (pregled/promena)"]
   ["-t" "--vreme DATETIME" "Vreme merenja (pregled/promena)"
    :validate [#(valid-datetime? %) "Vreme mora biti u formatu \"yyyy-MM-dd HH:mm:ss\""]]
   ["-v" "--vrednost DOUBLE" "Naziv merenja (pregled/promena)"
    :parse-fn #(Double/parseDouble %)]
   ["-l" "--limit INT" "Maksimalan broj prikazanih podataka (pregled)"
    :default 10
    :parse-fn #(Integer/parseInt %)
    :validate [#(and (<= % 1000) (>= % 1)) "Broj mora biti izmedju 0 i 1000"]]
   ["-o" "--offset INT" "Redni broj reda rezultata od kojeg pocinje listanje rezultata (pregled)"
    :default 0
    :parse-fn #(Integer/parseInt %)
    :validate [#(and (<= % 1000) (>= % 1)) "Broj mora biti izmedju 0 i 1000"]]
   ["-h" "--help"]])

(def help
  (str/join "\n" ["LISTA KOMANDI:"
                  "Izabrati samo jednu!"
                  ""
                  " unos      Unos merenja u bazu."
                  " pregled   Pregled merenja iz baze."
                  " brisanje  Brisanje merenja iz baze."
                  " promena   Promena merenja u bazi prema ID-u."]))

(defn check-db []
  (jdbc/execute! db ["CREATE TABLE IF NOT EXISTS merenje (
                      id VARCHAR(36) NOT NULL PRIMARY KEY,
                      naziv_merenja VARCHAR(100) NOT NULL,
                      vreme_merenja DATETIME NOT NULL,
                      vrednost_merenja DOUBLE NOT NULL,
                      vreme_unosa DATETIME NOT NULL,
                      vreme_promene DATETIME NOT NULL
                      )"]))

(defn error-msg [s]
  (if (vector? s)
    (println (str/join "\n" s) "\nKoristite --help za pomoc.")
    (println s "\nKoristite --help za pomoc.")))


(defn unos [args]
  (if (= (count args) 3)
    (let [[name time value] args
          id (java.util.UUID/randomUUID)
          timestamp (timestamp)]
      (sql/insert! db :merenje
                   {:id               id
                    :naziv_merenja    name
                    :vreme_merenja    time
                    :vrednost_merenja value
                    :vreme_unosa      timestamp
                    :vreme_promene    timestamp}))
    (error-msg "Usage: unos <naziv_merenja (string)> <vreme_merenja (\"yyyy-MM-dd HH:mm:ss\")> <vrednost_merenja (double)>")))

(defn pregled [opts]
  (let [{:keys [id naziv vreme vrednost limit offset]} opts]
    (when (or id naziv vreme vrednost)
      (let [filtered-opts (->> {:id               id
                                :naziv_merenja    naziv
                                :vreme_merenja    vreme
                                :vrednost_merenja vrednost}
                               (remove #(nil? (val %)))
                               (into {}))]
        (->> (sql/find-by-keys db :merenje filtered-opts {:limit limit :offset offset})
             (ds/->dataset)
             (ds.print/dataset->str)
             (println))
        ))))

(defn brisanje [opts]
  (let [id (:id opts)]
    (if (and (= (count opts) 3) id)                         ; Count opts 3 jer limit i offset imaju default vrednosti
      ((sql/delete! db :merenje {:id id})
       (println "Uspesno brisanje merenja id " id "!"))
      (error-msg "Komanda za brisanje prihvata samo --id opciju!"))))

(defn promena [opts]
  (if (and (>= (count opts) 4) (:id opts))                  ; Count opts 4 zbog limit i offset
    (let [{:keys [id naziv vreme vrednost]} opts
          filtered-opts (->> {:naziv_merenja    naziv
                              :vreme_merenja    vreme
                              :vrednost_merenja vrednost
                              :vreme_promene    (timestamp)}
                             (remove #(nil? (val %)))
                             (into {}))]
      (sql/update! db :merenje filtered-opts {:id id})
      (println "Uspesno izmenjeno merenje id " id "!"))
    (error-msg "Uneti minimum dve opcije, --id je obavezna!")))

(defn -main [& args]
  (check-db)
  (let [parsed-opts (parse-opts args cli-opts)
        arguments (:arguments parsed-opts)
        cmd (first arguments)
        opts (:options parsed-opts)
        errors (:errors parsed-opts)]
    (if (not errors)
      (case cmd
        "unos" (unos (rest arguments))
        "pregled" (pregled opts)
        "brisanje" (brisanje opts)
        "promena" (promena opts)
        (println "Nepoznata komanda, koristite --help za pomoc."))
      (error-msg errors))
    (when (:help opts)
      (println help "\nOPCIJE:\n" (:summary parsed-opts)))))
