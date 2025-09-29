// Import
const db = require("../models");
const _ = require("lodash");
const { v4: uuidv4 } = require("uuid");

//Table
const activity = db.activity;
const user = db.user;
const medal = db.medal;

// Common Function
const Op = db.Sequelize.Op;
const returnError = require("../common/error");
const returnSuccess = require("../common/success");
const returnSuccessMessage = require("../common/successMessage");
const common = require("../common/common");
const connection = require("../common/db");

// Input Validation
const validateactivityInput = require("../validation/activity-validation");

exports.list = async (req, res) => {
  let user = req.user.username;
  // default 10 records per page
  let limit = 10;
  if (req.query.limit) limit = parseInt(req.query.limit);

  // page offset
  let from = 0;
  if (!req.query.page) from = 0;
  else from = parseInt(req.query.page) * limit;

  // filters (where clause)
  let option = {};
  if (req.query.aType) {
    option.aType = req.query.aType;
  }
  option.username = user;


  if (req.query.from && !_.isEmpty("" + req.query.from)) {
    let fromDate = new Date(req.query.from);
    fromDate.setHours(0, 0, 0, 0);
    if (!_.isNaN(fromDate.getTime())) {
      if (req.query.to && !_.isEmpty("" + req.query.to)) {
        let toDate = new Date(req.query.to);
        toDate.setHours(23, 59, 59, 999);
        if (!_.isNaN(toDate.getTime())) {
          option.rDate = {
            [Op.and]: [{ [Op.gte]: fromDate }, { [Op.lte]: toDate }],
          };
        } else {
          option.rDate = {
            [Op.gte]: fromDate,
          };
        }
      } else {
        option.rDate = {
          [Op.gte]: fromDate,
        };
      }
    }
  } else if (req.query.to && !_.isEmpty("" + req.query.to)) {
    let toDate = new Date(req.query.to);
    toDate.setHours(23, 59, 59, 999);
    if (!_.isNaN(toDate.getTime())) {
      option.rDate = {
        [Op.lte]: toDate,
      };
    }
  }
  // if (req.query.search && !_.isEmpty(req.query.search)) {
  //   option[Op.or] = [
  //     { uuid: { [Op.like]: `%${req.query.search}%` } },
  //     { psmbrnam: { [Op.like]: `%${req.query.search}%` } },
  //     { psmbreml: { [Op.like]: `%${req.query.search}%` } },
  //   ];
  // }

  // if (req.query.psmbrtyp && !_.isEmpty(req.query.psmbrtyp)) {
  //   option.psmbrtyp = req.query.psmbrtyp;
  // }

  // //Sort and filter for psmbrpre
  // if (req.query.psmbrpre && !_.isEmpty(req.query.psmbrpre)) {
  //   option.psmbrpre = req.query.psmbrpre;
  // }
  const { count, rows } = await activity.findAndCountAll({
    limit: parseInt(limit),
    offset: from,
    where: option,
    raw: true,
    attributes: [
      ["uuid", "id"],
      "uuid",
      "aType",
      "username",
      "rDate",
      "distance",
      "duration_sec",
      "duration_min",
      "duration_hour",
      "openq1",
      "openq2",
      "openq3",
      "openq4",
      "openq5",
      "openq6",
      "openq7",
      "openq8",
    ],
    order: [["rDate", "desc"]],
  });

  let newRows = [];
  for (var i = 0; i < rows.length; i++) {
    let obj = rows[i];

    obj.rDate = await common.formatDateTime(obj.rDate, "/");
    obj.distance = await common.formatDecimal(obj.distance);

    newRows.push(obj);
  }

  if (count > 0)
    return returnSuccess(
      200,
      {
        total: count,
        data: newRows,
        extra: { file: "activity", key: ["uuid"] },
      },
      res
    );
  else return returnSuccess(200, { total: 0, data: [] }, res);
};

exports.findOne = async (req, res) => {
  const id = req.query.id ? req.query.id : "";
  if (!id || id == "") {
    return returnError(req, 500, "RECORDIDISREQUIRED", res);
  }
  try {
    const result = await activity.findOne({
      where: { uuid: id },
      raw: true,
    });

    if (!result) return returnError(req, 400, "NORECORDFOUND", res);

    return returnSuccess(200, result, res);
  } catch (err) {
    console.log("Error in findOne:", err);
    return returnError(req, 500, "UNEXPECTEDERROR", res);
  }
};

exports.create = async (req, res) => {
  const { errors, isValid } = validateactivityInput(req.body, "A");
  if (!isValid) return returnError(req, 400, errors, res);
  const { rDate, duration_sec, duration_min, duration_hour } = req.body;
  const baseDate = new Date(rDate);

  // Total offset in milliseconds
  const offsetMs =
    (duration_hour * 3600 + duration_min * 60 + duration_sec) * 1000;

  // Define window
  const startDate = new Date(baseDate.getTime() - offsetMs);
  const endDate = new Date(baseDate.getTime() + offsetMs);
  const exist = await activity.findOne({
    where: {
      username: req.user.username,
      rDate: {
        [Op.between]: [startDate, endDate]
      }
    },
    raw: true,
  });

  if (exist) {
    return returnError(req, 400, { rDate: "RECORDEXIST" }, res);
  }
  const aType = req.body.aType;
  const distance = req.body.distance;
  switch (req.body.aType) {
    case 'S': //Swim
    case 'H': //Hike
    case 'W': //Walk
    case 'C': //Climb
    case 'D': //Dance
    case 'B': //Cycling
      break;
    default:
      return returnError(req, 500, { aType: "aType not correct" }, res);

  }
  const t = await connection.sequelize.transaction();

  try {
    activity
      .create(
        {
          uuid: uuidv4(),
          username: req.user.username,
          aType: req.body.aType,
          distance: req.body.distance,
          rDate: new Date(),
          duration_hour: req.body.duration_hour,
          duration_sec: req.body.duration_sec,
          duration_min: req.body.duration_min,
          openq1: req.body.openq1,
          openq2: req.body.openq2,
          openq3: req.body.openq3,
          openq4: req.body.openq4,
          openq5: req.body.openq5,
          openq6: req.body.openq6,
          openq7: req.body.openq7,
          openq8: req.body.openq8,
        }, { transaction: t }
      )
      .then(async (data) => {
        try {

          let isMedal = await medal.findOne({
            where: {
              username: req.user.username
            }, raw: true
          });

          if (isMedal && isMedal.username == req.user.username) {
            await medal.update(
              {
                medal1: (aType == "W" && distance >= 2) || isMedal.medal1 == "Y" ? "Y" : "N",
                medal2: (aType == "W" && distance >= 5) || isMedal.medal2 == "Y" ? "Y" : "N",
                medal3: (aType == "W" && distance >= 10) || isMedal.medal3 == "Y" ? "Y" : "N",
                medal4: aType == "H" || isMedal.medal4 == "Y" ? "Y" : "N",
                medal5: (aType == "S" && distance >= 0.1) || isMedal.medal5 == "Y" ? "Y" : "N",
                medal6: (aType == "S" && distance >= 0.2) || isMedal.medal6 == "Y" ? "Y" : "N",
                medal7: (aType == "S" && distance >= 0.3) || isMedal.medal7 == "Y" ? "Y" : "N",
                medal8: aType == "C" || isMedal.medal8 == "Y" ? "Y" : "N",
                medal9: aType == "D" || isMedal.medal9 == "Y" ? "Y" : "N",
                medal10: (aType == "B" && distance >= 10) || isMedal.medal10 == "Y" ? "Y" : "N",
                medal11: (aType == "B" && distance >= 30) || isMedal.medal11 == "Y" ? "Y" : "N",
                medal12: (aType == "B" && distance >= 50) || isMedal.medal12 == "Y" ? "Y" : "N",

              }, {
              where: {
                username: req.user.username
              }
            }
            )
          } else {
            medal.create({
              username: req.user.username,
              medal1: aType == "W" && distance >= 2 ? "Y" : "N",
              medal2: aType == "W" && distance >= 5 ? "Y" : "N",
              medal3: aType == "W" && distance >= 10 ? "Y" : "N",
              medal4: aType == "H" ? "Y" : "N",
              medal5: aType == "S" && distance >= 0.1 ? "Y" : "N",
              medal6: aType == "S" && distance >= 0.2 ? "Y" : "N",
              medal7: aType == "S" && distance >= 0.3 ? "Y" : "N",
              medal8: aType == "C" ? "Y" : "N",
              medal9: aType == "D" ? "Y" : "N",
              medal10: aType == "B" && distance >= 10 ? "Y" : "N",
              medal11: aType == "B" && distance >= 30 ? "Y" : "N",
              medal12: aType == "B" && distance >= 50 ? "Y" : "N",
            })
          }
        } catch (error) {
          console.log(error);
          await t.rollback();
          return returnError(req, 500, "UNEXPECTEDERROR", res);
        }

        await t.commit();
        return returnSuccess(200, { message: "Record has been created", recordId: data.uuid }, res);
      })
      .catch(async (err) => {
        console.log(err);
        await t.rollback();
        return returnError(req, 500, "UNEXPECTEDERROR", res);
      });
  } catch (err) {
    console.log("Error in create:", err);
    return returnError(req, 500, "UNEXPECTEDERROR", res);
  }
};




exports.listMedal = async (req, res) => {
  const id = req.user.username ? req.user.username : "";
  if (!id || id == "") {
    return returnError(req, 500, "RECORDIDISREQUIRED", res);
  }
  try {
    const result = await medal.findOne({
      where: { username: id },
      raw: true,
    });

    if (!result) return returnSuccess(200, {
      username: req.user.username,
      medal1: "N",
      medal2: "N",
      medal3: "N",
      medal4: "N",
      medal5: "N",
      medal6: "N",
      medal7: "N",
      medal8: "N",
      medal9: "N",
      medal10: "N",
      medal11: "N",
      medal12: "N",
    }, res);

    return returnSuccess(200, result, res);
  } catch (err) {
    console.log("Error in findOne:", err);
    return returnError(req, 500, "UNEXPECTEDERROR", res);
  }
};


// exports.update = async (req, res) => {
//   let id = req.user.uuid;
//   if (!id) {
//     id = req.body.id;
//   }
//   if (!id) {
//     return returnError(req, 500, "RECORDIDISREQUIRED", res);
//   }

//   const { errors, isValid } = validateactivityInput(req.body, "C");
//   if (!isValid) return returnError(req, 400, errors, res);

//   try {
//     const exist = await activity.findOne({
//       where: { uuid: id },
//       raw: true,
//     });

//     if (!exist) return returnError(req, 400, "NORECORDFOUND", res);

//     // 3. gENCODE Validation
//     let ddlErrors = {};
//     let err_ind = false;

//     if (!_.isEmpty(req.body.psmbrtyp)) {
//       let yesorno = await common.retrieveSpecificGenCodes(
//         req,
//         "MBRTYP",
//         req.body.psmbrtyp
//       );
//       if (!yesorno || !yesorno.prgedesc) {
//         ddlErrors.psmbrtyp = "INVALIDDATAVALUE";
//         err_ind = true;
//       }
//     }

//     if (!_.isEmpty(req.body.psmbrpre)) {
//       let yesorno = await common.retrieveSpecificGenCodes(
//         req,
//         "HPPRE",
//         req.body.psmbrpre
//       );
//       if (!yesorno || !yesorno.prgedesc) {
//         ddlErrors.psmbrpre = "INVALIDDATAVALUE";
//         err_ind = true;
//       }
//     }

//     if (err_ind) return returnError(req, 400, ddlErrors, res);
//     // Check user existence
//     const validateUser = await user.findOne({
//       where: {
//         psusrunm: req.user.psusrunm,
//       },
//       raw: true,
//       attributes: ["psusrunm", "psusrnam"],
//     });

//     if (!validateUser) {
//       return returnError(req, 400, { psusrnme: "NORECORDFOUND" }, res);
//     }

//     const t = await connection.sequelize.transaction();

//     await activity
//       .update(
//         {
//           // uuid: reference,
//           psmbrnam: req.body.psmbrnam,
//           psmbreml: req.body.psmbreml,
//           psmbrdob: req.body.psmbrdob,
//           // psmbrpts: req.body.psmbrpts,
//           // distance: req.body.distance,
//           // psmbrtyp: req.body.psmbrtyp,
//           // psmbrexp: req.body.psmbrexp,
//           rDate: req.body.rDate,
//           // psmbrcar: req.body.psmbrcar,
//           //psusrnme: req.body.psusrnme,
//           //psmbrpre: req.body.psmbrpre,
//           psmbrphn: req.body.psmbrphn,
//           mntuser: req.user.psusrunm,
//         },
//         { where: { uuid: id } }, { transaction: t }
//       )
//       .then(async () => {

//         await user.update(
//           {
//             psusrnam: req.body.psmbrnam,
//             psusrphn: req.body.psmbrphn,
//             psusreml: req.body.psmbreml,
//           },
//           { where: { psusrunm: req.user.psusrunm } }
//         )
//         await t.commit();
//         // common.writeMntLog("activity", null, null, id, "C", req.user.psusrunm);

//         return returnSuccessMessage(req, 200, "UPDATESUCCESSFUL", res);
//       })
//       .catch(async (err) => {
//         console.log("This is the unx error", err);
//         await t.rollback();
//         return returnError(req, 500, "UNEXPECTEDERROR", res);
//       });
//   } catch (err) {
//     console.log("Error in update:", err);
//     return returnError(req, 500, "UNEXPECTEDERROR", res);
//   }
// };

// exports.delete = async (req, res) => {
//   const id = req.body.id ? req.body.id : "";
//   if (!id || id == "") {
//     return returnError(req, 500, "RECORDIDISREQUIRED", res);
//   }

//   try {
//     const t = await connection.sequelize.transaction();

//     const exist = await activity.findOne({
//       where: { uuid: id },
//       raw: true,
//     });

//     if (!exist) return returnError(req, 400, "NORECORDFOUND", res);

//     await activity
//       .destroy(
//         {
//           where: { uuid: id },
//         },
//         { transaction: t }
//       )
//       .then(async () => {
//         await psmbrcrt.destroy({
//           where: {
//             psmbrcar: exist.psmbrcar,
//           },
//         });

//         t.commit();
//         common.writeMntLog(
//           "activity",
//           null,
//           null,
//           id,
//           "D",
//           req.user.psusrunm,
//           "",
//           id
//         );
//       })
//       .catch((err) => {
//         console.log(err);
//         t.rollback();
//         return returnError(req, 500, "UNEXPECTEDERROR", res);
//       });

//     return returnSuccessMessage(req, 200, "DELETESUCCESSFUL", res);
//   } catch (err) {
//     console.log("Error in delete:", err);
//     return returnError(req, 500, "UNEXPECTEDERROR", res);
//   }
// };

