import { execSync } from "node:child_process";

const blocked = /\.(png|jpg|jpeg|webp|wav|mp3|ttf|otf|exe|apk|aab|zip|msi)$/i;
const files = execSync("git ls-files .", { encoding: "utf8" }).split("\n").filter(Boolean);
const offenders = files.filter((f) => blocked.test(f));
if (offenders.length) {
  console.error("Binary files are forbidden:\n" + offenders.join("\n"));
  process.exit(1);
}
console.log("PASS binary guard");
